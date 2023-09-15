import os
import threading
import time
import pandas as pd
import numpy as np
from pathlib import Path
from multiprocessing import shared_memory
import gzip
import io
import hashlib
from datetime import datetime
from tqdm import tqdm
import threading

from SharedData.Logger import Logger
from SharedData.AWSS3 import S3Upload, S3Download, UpdateModTime, S3ListFolder
from SharedData.TableIndex import TableIndex
from SharedData.SharedNumpy import SharedNumpy
from SharedData.RealTime import RealTime

if os.name == 'posix':
    from SharedData.Utils import cpp


class Table:
    # TODO: create a on disk mode

    def __init__(self, shareddata, database, period, source, tablename,
                 records=None, names=None, formats=None, size=None, overwrite=False, user='master'):
        self.shareddata = shareddata
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename

        self.subscription_thread = None
        self.index = TableIndex(self)

        self.init_time = time.time()
        self.download_time = pd.NaT

        # file partitioning threshold
        self.maxtailbytes = int(100*10**6)

        # head header
        self.hdrnames = ['headersize', 'headerdescr', 'semaphore', 'md5hash', 'mtime', 'itemsize', 'recordssize', 'count',
                         'headsize', 'pkeysize', 'minchgid', 'hastail', 'descr']
        self.hdrformats = ['<i8', '|S250', '<u1', '|S16', '<f8', '<i8', '<i8', '<i8',
                           '<i8', '<i8', '<i8', '<u1', '|S400']
        self.hdrdtype = np.dtype(
            {'names': self.hdrnames, 'formats': self.hdrformats})
        self.hdr = np.recarray(shape=(1,), dtype=self.hdrdtype)[0]
        self.hdr['headsize'] = 0  # initialize headers
        # tail header
        self.tailhdrnames = ['headersize', 'headerdescr',
                             'md5hash', 'mtime', 'tailsize']
        self.tailhdrformats = ['<i8', '|S80', '|S16', '<f8', '<i8']
        self.tailhdrdtype = np.dtype(
            {'names': self.tailhdrnames, 'formats': self.tailhdrformats})
        self.tailhdr = np.recarray(shape=(1,), dtype=self.tailhdrdtype)[0]
        self.tailhdr['tailsize'] = 0  # initialize headers
        self.tailhdr['headersize'] = 80
        _headerdescr = ','.join(self.tailhdrnames) + \
            ';'+','.join(self.tailhdrformats)
        _headerdescr_b = str.encode(
            _headerdescr, encoding='UTF-8', errors='ignore')
        self.tailhdr['headerdescr'] = _headerdescr_b

        # records
        self.recnames = []
        self.recformats = []
        self.recdtype = None
        self.records = np.ndarray([])
        # shared memory
        self.shm = None
        # path
        self.shm_name = self.user + '/' + self.database + '/' \
            + self.period + '/' + self.source + '/table/' + self.tablename
        if os.name == 'posix':
            self.shm_name = self.shm_name.replace('/', '\\')

        self.relpath = user+'/'+database+'/'+period+'/'+source+'/table/'+tablename

        self.path = Path(os.environ['DATABASE_FOLDER'])
        self.path = self.path / self.user
        self.path = self.path / self.database
        self.path = self.path / self.period
        self.path = self.path / self.source
        self.path = self.path / 'table'
        self.path = self.path / self.tablename
        self.path = Path(str(self.path).replace('\\', '/'))
        if self.shareddata.save_local:
            os.makedirs(self.path, exist_ok=True)

        self.headpath = self.path / 'head.bin'
        self.tailpath = self.path / 'tail.bin'

        self.exists = False
        if self.ismalloc():
            self.create_map = 'map'
            self.exists = True
        else:
            self.create_map = 'create'
            if self.headpath.exists():
                self.exists = True
            else:
                keys = S3ListFolder(self.shm_name.replace('\\', '/'))
                if len(keys) > 0:
                    self.exists = True

        # initalize
        try:
            if self.create_map == 'create':
                if (not self.exists):
                    if (not records is None):
                        # create new shared memory set value
                        if isinstance(records, pd.DataFrame):
                            records = self.df2records(records)
                        descr = records.__array_interface__['descr']
                        names = [item[0] for item in descr]
                        formats = [item[1] for item in descr]
                        if size is None:
                            size = int(records.size)
                        self.create(names, formats, size)
                        self.records.insert(records)

                    elif (not names is None) & (not formats is None)\
                            & (not size is None):
                        # create new shared memory empty
                        self.create(names, formats, size)
                    else:
                        raise Exception(
                            '%s not found create first!' % (self.relpath))

                elif (self.exists):
                    if not overwrite:
                        if not self.read(size):
                            raise Exception('%s failed to read!' %
                                            (self.relpath))
                    else:
                        if (not records is None):
                            # create new shared memory set value
                            if isinstance(records, pd.DataFrame):
                                records = self.df2records(records)
                            descr = records.__array_interface__['descr']
                            names = [item[0] for item in descr]
                            formats = [item[1] for item in descr]
                            if size is None:
                                size = int(records.size)
                            self.create(names, formats, size)
                            self.records.insert(records)

                        elif (not names is None) & (not formats is None)\
                                & (not size is None):
                            # create new shared memory empty
                            self.create(names, formats, size)
                        else:
                            raise Exception(
                                '%s failed to overwrite!' % (self.relpath))

            elif (self.create_map == 'map'):
                # map existing shared memory
                self.malloc_map()
        except Exception as e:
            self.free()
            msg = '%s error initalizing!' % self.relpath
            Logger.log.error(msg)
            raise Exception(msg)
        
        self.index.initialize()

        self.init_time = time.time() - self.init_time

    def ismalloc(self):
        [self.shm, ismalloc] = self.shareddata.malloc(self.shm_name)
        return ismalloc

    ############### CREATE ###############

    def create(self, names, formats, size):

        check_pkey = True
        npkeys = len(self.index.pkeycolumns)
        for k in range(npkeys):
            check_pkey = (check_pkey) & (names[k] == self.index.pkeycolumns[k])
        if not check_pkey:
            raise Exception('First columns must be %s!' %
                            (self.index.pkeycolumns))
        else:
            if not 'mtime' in names:
                names.insert(npkeys, 'mtime')
                formats.insert(npkeys, '<M8[ns]')

            # malloc recarray
            self.recnames = names
            self.rectypes = formats
            self.recdtype = np.dtype(
                {'names': self.recnames, 'formats': self.rectypes})
            descr_str = ','.join(self.recnames)+';'+','.join(self.rectypes)
            descr_str_b = str.encode(
                descr_str, encoding='UTF-8', errors='ignore')
            len_descr = len(descr_str_b)

            # build header
            self.hdrnames = ['headersize', 'headerdescr', 'semaphore', 'md5hash', 'mtime', 'itemsize', 'recordssize', 'count',
                             'headsize', 'minchgid', 'hastail', 'descr']
            self.hdrformats = ['<i8', '|S250', '<u1', '|S16', '<f8', '<i8', '<i8', '<i8',
                               '<i8', '<i8', '<u1', '|S'+str(len_descr)]
            hdrnames = ','.join(self.hdrnames)
            hdrdtypes = ','.join(self.hdrformats)
            hdrdescr_str = hdrnames+';'+hdrdtypes
            hdrdescr_str_b = str.encode(
                hdrdescr_str, encoding='UTF-8', errors='ignore')

            self.hdrdtype = np.dtype(
                {'names': self.hdrnames, 'formats': self.hdrformats})
            self.hdr = np.recarray(shape=(1,), dtype=self.hdrdtype)[0]
            self.hdr['headersize'] = 250
            self.hdr['headerdescr'] = hdrdescr_str_b
            self.hdr['mtime'] = datetime.now().timestamp()
            self.hdr['count'] = 0
            self.hdr['minchgid'] = self.hdr['count']
            self.hdr['itemsize'] = int(self.recdtype.itemsize)
            self.hdr['recordssize'] = int(size)
            self.hdr['headsize'] = 0
            self.hdr['descr'] = descr_str_b

            # create memory space
            self.malloc_create()
            self.release()  # release semaphore

    def malloc_create(self):
        nb_hdr = self.hdrdtype.itemsize  # number of header bytes
        # number of data bytes
        nb_records = int(self.hdr['recordssize']*self.hdr['itemsize'])
        total_size = int(nb_hdr+nb_records)

        # if in linux check if data exists and dispose it
        # doesnt work in windows
        [self.shm, ismalloc] = \
            self.shareddata.malloc(
                self.shm_name, create=True, size=total_size, overwrite=True)
        if not ismalloc:
            raise Exception('Could not allocate shared memory!')

        # allocate header
        self.hdr['semaphore'] = 1  # lock semaphore memory
        self.shm.buf[0:nb_hdr] = self.hdr.tobytes()
        self.hdr = np.ndarray((1,), dtype=self.hdrdtype,
                              buffer=self.shm.buf)[0]
        # allocate table data
        descr = self.hdr['descr'].decode(encoding='UTF-8', errors='ignore')
        self.recnames = descr.split(';')[0].split(',')
        self.recformats = descr.split(';')[1].split(',')
        self.recdtype = np.dtype(
            {'names': self.recnames, 'formats': self.recformats})
        self.records = SharedNumpy((self.hdr['recordssize'],),
                                   dtype=self.recdtype, buffer=self.shm.buf, offset=nb_hdr)
        self.records.table = self
        self.records.preallocate()

    def malloc_map(self):
        # Read the header
        nbhdrdescr = int.from_bytes(self.shm.buf[0:8], byteorder='little')
        hdrdescr_b = self.shm.buf[8:8+nbhdrdescr].tobytes()
        hdrdescr = hdrdescr_b.decode(encoding='UTF-8', errors='ignore')
        hdrdescr = hdrdescr.replace('\x00', '')
        self.hdrnames = hdrdescr.split(';')[0].split(',')
        self.hdrformats = hdrdescr.split(';')[1].split(',')
        self.hdrdtype = np.dtype(
            {'names': self.hdrnames, 'formats': self.hdrformats})
        nb_hdr = self.hdrdtype.itemsize
        self.hdr = np.ndarray((1,), dtype=self.hdrdtype,
                              buffer=self.shm.buf)[0]

        descr = self.hdr['descr'].decode(encoding='UTF-8', errors='ignore')
        self.recnames = descr.split(';')[0].split(',')
        self.recformats = descr.split(';')[1].split(',')
        self.recdtype = np.dtype(
            {'names': self.recnames, 'formats': self.recformats})
        self.records = SharedNumpy((self.hdr['recordssize'],),
                                   dtype=self.recdtype, buffer=self.shm.buf, offset=nb_hdr)
        self.records.table = self

    def free(self):
        self.shareddata.free(self.shm_name)
        self.shareddata.free(self.shm_name+'#pkey')
        self.shareddata.free(self.shm_name+'#dateidx')
        self.shareddata.free(self.shm_name+'#symbolidx')        
        self.shareddata.free(self.shm_name+'#portidx')
        self.shareddata.free(self.shm_name+'#dtportidx')

    ############### READ ###############

    def read(self, size=None):
        head_io = None
        tail_io = None

        # open head_io to read header
        # download remote head if its newer than local
        if self.shareddata.s3read:
            [head_io, head_remote_mtime] = self.download_head()

        # open head_io to read header
        if self.shareddata.save_local:
            if head_io is None:
                if self.headpath.exists():
                    head_io = open(self.headpath, 'rb')

        # read table
        if not head_io is None:
            self.read_header(head_io)

            if self.shareddata.s3read:
                if self.hdr['hastail'] == 1:
                    [tail_io, tail_remote_mtime] = self.download_tail()

            if self.shareddata.save_local:
                if self.hdr['hastail'] == 1:
                    if tail_io is None:
                        if self.tailpath.exists():
                            tail_io = open(self.tailpath, 'rb')

            # read tail header if exists
            if not tail_io is None:
                self.read_tail_header(tail_io)

            if size is None:
                self.hdr['recordssize'] = int(
                    self.hdr['count']*1.25)  # add 25% space for growth
            else:
                self.hdr['recordssize'] = int(size)
            # malloc create shared memory with recordssize rows
            self.malloc_create()

            # read head data to shared memory
            head_md5 = self.read_head(head_io)
            if not self.compare_hash(self.hdr['md5hash'],head_md5.digest()):
                Logger.log.error('Head corrupted %s!' % (self.headpath))
                raise Exception('Head corrupted %s!' % (self.headpath))
            elif isinstance(head_io, gzip.GzipFile) \
                    & (self.shareddata.save_local):
                self.write_head(head_remote_mtime)
                UpdateModTime(self.headpath, head_remote_mtime)

            # read tail data to shared memory
            if not tail_io is None:
                tail_md5 = self.read_tail(tail_io)
                if not self.compare_hash(self.tailhdr['md5hash'],tail_md5.digest()):
                    Logger.log.error('Tail corrupted %s!' % (self.tailpath))
                    raise Exception('Tail corrupted %s!' % (self.tailpath))
                elif (isinstance(tail_io, gzip.GzipFile)) \
                        & (self.shareddata.save_local):
                    self.write_tail(tail_remote_mtime)
                    UpdateModTime(self.tailpath, tail_remote_mtime)

            # recalculate count
            self.hdr['count'] = self.hdr['headsize']+self.tailhdr['tailsize']
            self.hdr['minchgid'] = self.hdr['count']

            self.release()

        return (not head_io is None)

    def download_head(self):
        head_io = None
        force_download = (not self.shareddata.save_local)
        tini = time.time()
        [head_io_gzip, head_local_mtime, head_remote_mtime] = \
            S3Download(str(self.headpath), str(
                self.headpath)+'.gzip', force_download)
        if not head_io_gzip is None:
            te = time.time()-tini+0.000001
            datasize = head_io_gzip.getbuffer().nbytes/1000000
            Logger.log.debug('download head %s %.2fMB in %.2fs %.2fMBps ' %
                             (self.relpath, datasize, te, datasize/te))
            head_io_gzip.seek(0)
            head_io = gzip.GzipFile(fileobj=head_io_gzip, mode='rb')
        return [head_io, head_remote_mtime]

    def read_header(self, head_io):
        head_io.seek(0)
        nbhdrdescr = int.from_bytes(head_io.read(8), byteorder='little')
        hdrdescr_b = head_io.read(nbhdrdescr)
        hdrdescr = hdrdescr_b.decode(encoding='UTF-8', errors='ignore')
        hdrdescr = hdrdescr.replace('\x00', '')
        self.hdrnames = hdrdescr.split(';')[0].split(',')
        self.hdrformats = hdrdescr.split(';')[1].split(',')
        self.hdrdtype = np.dtype(
            {'names': self.hdrnames, 'formats': self.hdrformats})
        nb_hdr = self.hdrdtype.itemsize
        head_io.seek(0)
        self.hdr = np.ndarray((1,), dtype=self.hdrdtype,
                              buffer=head_io.read(nb_hdr))[0]
        self.hdr = self.hdr.copy()
        self.hdr['semaphore'] = 1

    def download_tail(self):
        tail_io = None
        force_download = (not self.shareddata.save_local)
        tini = time.time()
        [tail_io_gzip, tail_local_mtime, tail_remote_mtime] = \
            S3Download(str(self.tailpath), str(
                self.tailpath)+'.gzip', force_download)
        if not tail_io_gzip is None:
            te = time.time()-tini+0.000001
            datasize = tail_io_gzip.getbuffer().nbytes/1000000
            Logger.log.debug('download tail %s %.2fMB in %.2fs %.2fMBps ' %
                             (self.relpath, datasize, te, datasize/te))
            tail_io_gzip.seek(0)
            tail_io = gzip.GzipFile(fileobj=tail_io_gzip, mode='rb')
        return [tail_io, tail_remote_mtime]

    def read_tail_header(self, tail_io):
        tail_io.seek(0)
        tailnbhdrdescr = int.from_bytes(tail_io.read(8), byteorder='little')
        tailhdrdescr_b = tail_io.read(tailnbhdrdescr)
        tailhdrdescr = tailhdrdescr_b.decode(encoding='UTF-8', errors='ignore')
        tailhdrdescr = tailhdrdescr.replace('\x00', '')
        self.tailhdrnames = tailhdrdescr.split(';')[0].split(',')
        self.tailhdrformats = tailhdrdescr.split(';')[1].split(',')
        self.tailhdrdtype = np.dtype(
            {'names': self.tailhdrnames, 'formats': self.tailhdrformats})

        nbtailhdr = self.tailhdrdtype.itemsize
        tail_io.seek(0)
        tailheader_buf = tail_io.read(nbtailhdr)
        self.tailhdr = np.ndarray((1,),
                                  dtype=self.tailhdrdtype, buffer=tailheader_buf)[0]
        self.tailhdr = self.tailhdr.copy()
        self.tailhdr['headersize'] = tailnbhdrdescr
        self.hdr['count'] = self.hdr['headsize']+self.tailhdr['tailsize']

    def read_head(self, head_io):
        # read head data to shared memory
        nb_hdr = self.hdrdtype.itemsize
        head_io.seek(nb_hdr)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_head_mb = nb_head / (1024*1024)
        block_size = 100 * 1024 * 1024  # or any other block size that you prefer
        head_md5 = hashlib.md5()
        if isinstance(head_io, gzip.GzipFile):
            message = 'Unzipping:%iMB %s' % (nb_head_mb, self.relpath)
        else:
            message = 'Reading:%iMB %s' % (nb_head_mb, self.relpath)
        # Use a with block to manage the progress bar
        with tqdm(total=nb_head, unit='B', unit_scale=True, desc=message) as pbar:
            read_bytes = 0
            # Loop until we have read all the data
            while read_bytes < nb_head:
                # Read a block of data
                chunk_size = min(block_size, nb_head-read_bytes)
                # Update the shared memory buffer with the newly read data
                ib = nb_hdr+read_bytes
                eb = nb_hdr+read_bytes+chunk_size
                self.shm.buf[ib:eb] = head_io.read(chunk_size)
                # Update the md5 hash value
                head_md5.update(self.shm.buf[ib:eb])
                # update the total number of bytes read so far
                read_bytes += chunk_size
                # Update the progress bar
                pbar.update(chunk_size)

        return head_md5

    def read_tail(self, tail_io):
        nb_hdr = self.hdrdtype.itemsize
        nb_tail = int(self.tailhdr['tailsize']*self.hdr['itemsize'])
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        ib = nb_hdr+nb_head
        eb = nb_hdr+nb_head+nb_tail
        self.shm.buf[ib:eb] = tail_io.read(nb_tail)
        # Update the md5 hash value
        tail_md5 = hashlib.md5()
        tail_md5.update(self.shm.buf[ib:eb])

        return tail_md5

    def compare_hash(self,h1,h2):
        l1 = len(h1)
        l2 = len(h2)
        l = min(l1,l2)
        return h1[:l]==h2[:l]
    ############### WRITE ###############

    def write(self):
        try:
            self.acquire()
            tini = time.time()
            # create header
            mtime = self.hdr['mtime']
            write_head = self.fill_header()

            # Create the thread targets
            def write_s3():
                if self.shareddata.s3write:
                    if write_head:
                        self.upload_head(mtime)

                    if self.hdr['hastail'] == 1:
                        self.upload_tail(mtime)

            def write_local():
                if self.shareddata.save_local:
                    if write_head:
                        self.write_head(mtime)

                    if self.hdr['hastail'] == 1:
                        self.write_tail(mtime)

            # Start the threads
            thread_s3 = threading.Thread(target=write_s3)
            thread_local = threading.Thread(target=write_local)

            thread_s3.start()
            thread_local.start()

            # Wait for both threads to complete
            thread_s3.join()
            thread_local.join()

            self.release()

            te = time.time() - tini
            datasize = self.hdr['count'] * self.hdr['itemsize'] / 1000000
            Logger.log.debug('write %s %.2fMB in %.2fs %.2fMBps ' %
                             (self.relpath, datasize, te, datasize / te))
        except Exception as e:
            self.release()
            Logger.log.error('Could not write %s\n%s!' % (self.path, e))
            raise Exception('Could not write %s\n%s!' % (self.path, e))

        return True

    def fill_header(self):

        # partition data by current year
        partdate = pd.Timestamp(datetime(datetime.now().year, 1, 1))
        idx = self.records['date'] >= partdate
        if np.any(idx):  # there is data for the current year
            if np.all(idx):  # all data for the current year
                headsize = self.hdr['count']
                tailsize = 0
                self.hdr['hastail'] = 0
            else:  # some data for the current year
                partid = np.where(idx)[0][0]
                headsize = partid
                tailsize = self.hdr['count'] - partid
                self.hdr['hastail'] = 1
        else:  # there is not data for the current year
            tailsize = 0
            headsize = self.hdr['count']
            self.hdr['hastail'] = 0

        headsize_chg = (headsize != self.hdr['headsize'])
        self.hdr['headsize'] = headsize

        head_modified = (self.hdr['minchgid'] <= self.hdr['headsize'])
        write_head = (head_modified) | (headsize_chg)

        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(tailsize*self.hdr['itemsize'])

        self.tailhdr['mtime'] = self.hdr['mtime']
        self.tailhdr['tailsize'] = tailsize

        if write_head:
            self.hdr['md5hash'] = 0  # reset the hash value
            nb_records_mb = (nb_header+nb_head)/(1024*1024)
            if nb_records_mb <= 100:
                m = hashlib.md5(self.shm.buf[nb_header:nb_header+nb_head])
            else:
                message = 'Creating md5 hash:%iMB %s' % (
                    nb_records_mb, self.relpath)
                block_size = 100 * 1024 * 1024  # or any other block size that you prefer
                nb_total = nb_header+nb_head
                read_bytes = nb_header
                m = hashlib.md5()
                # Use a with block to manage the progress bar
                with tqdm(total=nb_total, unit='B', unit_scale=True, desc=message) as pbar:
                    # Loop until we have read all the data
                    while read_bytes < nb_total:
                        # Read a block of data
                        chunk_size = min(block_size, nb_total-read_bytes)
                        # Update the shared memory buffer with the newly read data
                        m.update(
                            self.shm.buf[read_bytes:read_bytes+chunk_size])
                        read_bytes += chunk_size  # update the total number of bytes read so far
                        # Update the progress bar
                        pbar.update(chunk_size)
            self.hdr['md5hash'] = m.digest()

        if self.hdr['hastail'] == 1:
            self.tailhdr['md5hash'] = 0  # reset the hash value
            nb_records_mb = (nb_tail)/(1024*1024)
            startbyte = nb_header+nb_head
            if nb_records_mb <= 100:                
                m = hashlib.md5(self.shm.buf[startbyte:startbyte+nb_tail])
            else:
                message = 'Creating tail md5 hash:%iMB %s' % (
                    nb_records_mb, self.relpath)
                block_size = 100 * 1024 * 1024  # or any other block size that you prefer
                nb_total = nb_tail
                read_bytes = 0
                
                m = hashlib.md5()
                # Use a with block to manage the progress bar
                with tqdm(total=nb_total, unit='B', unit_scale=True, desc=message) as pbar:
                    # Loop until we have read all the data
                    while read_bytes < nb_total:
                        # Read a block of data
                        chunk_size = min(block_size, nb_total-read_bytes)
                        # Update the shared memory buffer with the newly read data
                        m.update(self.shm.buf[startbyte+read_bytes:startbyte+read_bytes+chunk_size])
                        read_bytes += chunk_size  # update the total number of bytes read so far
                        # Update the progress bar
                        pbar.update(chunk_size)

            self.tailhdr['md5hash'] = m.digest()

        return write_head

    def upload_head(self, mtime):
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        # zip head
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.shm.buf[0:nb_header])
            headsize_mb = nb_head / (1000000)
            blocksize = 1024*1024*100
            descr = 'Zipping:%iMB %s' % (headsize_mb, self.relpath)
            with tqdm(total=headsize_mb, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < nb_head:
                    # write in chunks of max 100 MB size
                    chunk_size = min(blocksize, nb_head-written)
                    gz.write(
                        self.shm.buf[nb_header+written:nb_header+written+chunk_size])
                    written += chunk_size
                    pbar.update(chunk_size)
        S3Upload(gzip_io, str(self.headpath)+'.gzip', mtime)

    def upload_tail(self, mtime):
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(self.tailhdr['tailsize']*self.hdr['itemsize'])
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.tailhdr.tobytes())
            gz.write(self.shm.buf[nb_header+nb_head:nb_header+nb_head+nb_tail])
        S3Upload(gzip_io, str(self.tailpath)+'.gzip', mtime)

    def write_head(self, mtime):
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        with open(self.headpath, 'wb') as f:
            f.write(self.shm.buf[0:nb_header])
            headsize_mb = nb_head / (1000000)
            blocksize = 1024*1024*100
            descr = 'Writing head:%iMB %s' % (headsize_mb, self.relpath)
            with tqdm(total=nb_head, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < nb_head:
                    # write in chunks of max 100 MB size
                    chunk_size = min(blocksize, nb_head-written)
                    ib = nb_header+written
                    eb = nb_header+written+chunk_size
                    f.write(self.shm.buf[ib:eb])
                    written += chunk_size
                    pbar.update(chunk_size)
            f.flush()
        os.utime(self.headpath, (mtime, mtime))

    def write_tail(self, mtime):
        nb_header = int(self.hdrdtype.itemsize)
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(self.tailhdr['tailsize']*self.hdr['itemsize'])

        with open(self.tailpath, 'wb') as f:
            f.write(self.tailhdr)
            tailsize_mb = nb_tail / (1000000)
            blocksize = 1024*1024*100  # 100 MB
            descr = 'Writing tail:%iMB %s' % (tailsize_mb, self.relpath)
            
            # Setup progress bar for tail
            with tqdm(total=nb_tail, unit='B', unit_scale=True, desc=descr) as pbar:
                written = 0
                while written < nb_tail:
                    # write in chunks of max 100 MB size
                    chunk_size = min(blocksize, nb_tail-written)
                    ib = nb_header+nb_head+written
                    eb = ib+chunk_size
                    f.write(self.shm.buf[ib:eb])
                    written += chunk_size
                    pbar.update(chunk_size)
            f.flush()
        os.utime(self.tailpath, (mtime, mtime))

    ############### CONVERT ###############

    def records2df(self, records):
        df = pd.DataFrame(records, copy=False)
        dtypes = df.dtypes.reset_index()
        dtypes.columns = ['tag', 'dtype']
        # convert object to string
        string_idx = ['|S' in str(dt) for dt in dtypes['dtype']]
        string_idx = (string_idx) | (dtypes['dtype'] == 'object')
        tags_obj = dtypes['tag'][string_idx].values
        for tag in tags_obj:
            try:
                df[tag] = df[tag].str.decode(encoding='utf-8', errors='ignore')
            except:
                pass
        df = df.set_index(self.index.pkeycolumns)
        return df

    def df2records(self, df):
        check_pkey = True
        if len(self.index.pkeycolumns) == len(df.index.names):
            for k in range(len(self.index.pkeycolumns)):
                check_pkey = (check_pkey) & (
                    df.index.names[k] == self.index.pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' %
                            (self.index.pkeycolumns))
        else:
            if self.recdtype is None:
                df = df.reset_index()
                dtypes = df.dtypes.reset_index()
                dtypes.columns = ['tag', 'dtype']
                # convert object to string
                tags_obj = dtypes['tag'][dtypes['dtype'] == 'object'].values
                for tag in tags_obj:
                    try:
                        df[tag] = df[tag].str.encode(
                            encoding='utf-8', errors='ignore')
                    except:
                        Logger.log.error('Could not convert %s!' % (tag))
                    df[tag] = df[tag].astype('|S')
                return np.ascontiguousarray(df.to_records(index=False))
            else:
                df = df.reset_index()
                dtypes = self.recdtype
                rec = np.full((df.shape[0],), fill_value=np.nan, dtype=dtypes)
                for col in dtypes.names:
                    try:
                        if col in df.columns:
                            rec[col] = df[col].astype(dtypes[col])
                    except Exception as e:
                        Logger.log.error(
                            'Could not convert %s!\n%s' % (col, e))

                return rec

    ############### LOCK ###############
    # TODO: set the PID of the process locking the semaphore
    # and check if the process is running to realease it otherwise
    def acquire(self):
        tini = time.time()
        if os.name == 'posix':
            # semaphore is process safe
            telapsed = 0
            hdrptr = self.hdr.__array_interface__['data'][0]
            semseek = 258
            while cpp.bool_compare_and_swap(hdrptr, semseek, 0, 1) == 0:
                telapsed = time.time() - tini
                if telapsed > 60:
                    Logger.log.warning('Waiting for semaphore...')
                    tini = time.time()
                time.sleep(0.000001)
        else:
            while self.hdr['semaphore'] != 0:
                telapsed = time.time() - tini
                if telapsed > 60:
                    Logger.log.warning('Waiting for semaphore...')
                    tini = time.time()
                time.sleep(0.0001)
            self.hdr['semaphore'] = 1

    def release(self):
        if os.name == 'posix':
            hdrptr = self.hdr.__array_interface__['data'][0]
            semseek = 258
            if cpp.bool_compare_and_swap(hdrptr, semseek, 1, 0) != 1:
                raise Exception('Tried to release semaphore without acquire!')
        else:
            self.hdr['semaphore'] = 0

    ############### SUBSCRIBE ###############

    def subscribe(self, host, port):
        if self.subscription_thread is None:
            self.subscription_thread = threading.Thread(
                target=RealTime.table_subscribe_thread,
                args=(self, host, port)
            )
            self.subscription_thread.start()
            Logger.log.debug('Subscription started!')
        else:
            Logger.log.error('Subscription already running!')
