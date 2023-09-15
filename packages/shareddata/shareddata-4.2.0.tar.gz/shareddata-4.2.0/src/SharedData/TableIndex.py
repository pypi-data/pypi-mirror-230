import numpy as np
import time
from multiprocessing import shared_memory


import SharedData.TableIndexJit as TableIndexJit
from SharedData.TableIndexJit import *
from SharedData.Logger import Logger


class TableIndex:

    def __init__(self, table):
        self.table = table
        self.shareddata = self.table.shareddata

        self.initialized = False

        # primary key hash table
        self.pkeycolumns = TableIndex.get_pkeycolumns(self.table.database)
        self.pkeystr = '_'.join(self.pkeycolumns)
        self.pkey = np.ndarray([])
        # date index
        self.dateiniidx = np.ndarray([])
        self.dateendidx = np.ndarray([])
        # symbol index
        self.symbollastidx = np.ndarray([])
        self.symbolprevidx = np.ndarray([])
        # portfolio index
        self.portlastidx = np.ndarray([])
        self.portprevidx = np.ndarray([])
        # date,portfolio index
        self.portiniidx = np.ndarray([])  # hash table
        self.portlist = np.ndarray([])  # linked list
        self.portlistcount = 0

    def initialize(self):                
        try:
            self.table.acquire()            
            self.get_functions()
            self.malloc()
            # check if index was created
            count = np.sum(self.pkey != -1)
            if self.table.hdr['count'] != count:
                self.create_index()
            self.initialized = True
        except Exception as e:
            Logger.log.error('Failed to intialize index for %s!\n%s' %
                             (self.table.relpath, str(e)))
            self.initialized = False
        finally:
            self.table.release()
            if not self.initialized:
                raise Exception('Failed to intialize index for %s!' %
                                (self.table.relpath))

    def get_functions(self):
        # primary key & index functions
        self.create_index_func = None
        self.upsert_func = None
        self.get_loc_func = None

        create_pkey_fname = 'create_pkey_' + self.pkeystr + '_jit'
        if hasattr(TableIndexJit, create_pkey_fname):
            self.create_index_func = getattr(TableIndexJit, create_pkey_fname)
        else:
            raise Exception('create_pkey function not found for database %s!'
                            % (self.table.database))

        upsert_fname = 'upsert_' + self.pkeystr + '_jit'
        if hasattr(TableIndexJit, upsert_fname):
            self.upsert_func = getattr(TableIndexJit, upsert_fname)
        else:
            raise Exception('upsert function not found for database %s!'
                            % (self.table.database))

        get_loc_fname = 'get_loc_' + self.pkeystr + '_jit'
        if hasattr(TableIndexJit, get_loc_fname):
            self.get_loc_func = getattr(TableIndexJit, get_loc_fname)
        else:
            raise Exception('get_loc function not found for database %s!'
                            % (self.table.database))

        if 'date_portfolio_' in self.pkeystr:
            self.get_index_date_portfolio_func = \
                getattr(TableIndexJit, 'get_index_date_portfolio_jit')

    def malloc(self):
        shm_name = self.table.shm_name
        self.malloc_pkey(shm_name)
        if 'date' in self.pkeystr:
            self.malloc_dateidx(shm_name)
        if 'symbol' in self.pkeystr:
            self.malloc_symbolidx(shm_name)
        if 'portfolio' in self.pkeystr:
            self.malloc_portfolioidx(shm_name)
        if 'date_portfolio_' in self.pkeystr:
            self.malloc_dateportfolioidx(shm_name)

    def malloc_pkey(self, shm_name):
        keysize = int(self.table.records.size*5)
        keysize_bytes = int(keysize * 4)

        iscreate = False
        [self.pkeyshm, ismalloc] = self.shareddata.malloc(shm_name+'#pkey')
        if not ismalloc:
            [self.pkeyshm, ismalloc] = self.shareddata.malloc(shm_name+'#pkey',
                                                              create=True, size=keysize_bytes)
            iscreate = True

        self.pkey = np.ndarray((keysize,), dtype=np.int32,
                               buffer=self.pkeyshm.buf)
        if iscreate:
            self.pkey[:] = -1

    def malloc_dateidx(self, shm_name):
        # date index
        dtunit = str(self.table.records.dtype[0]).split('[')[-1].split(']')[0]
        if dtunit == 'ns':
            self.dateunit = 24*60*60*1000*1000*1000
        else:
            raise Exception('Only dates with ns precision are supported!')
        maxdate = np.datetime64('2070-01-01', 'D')
        dateidxsize = maxdate.astype(int)
        dateidxsize_bytes = int(dateidxsize * 4)

        iscreate = False
        [self.dateidxshm, ismalloc] = self.shareddata.malloc(
            shm_name+'#dateidx')
        if not ismalloc:
            [self.dateidxshm, ismalloc] = self.shareddata.malloc(shm_name+'#dateidx',
                                                                 create=True, size=int(dateidxsize_bytes*2))
            iscreate = True

        self.dateiniidx = np.ndarray(
            (dateidxsize,), dtype=np.int32, buffer=self.dateidxshm.buf)
        self.dateendidx = np.ndarray((dateidxsize,), dtype=np.int32, buffer=self.dateidxshm.buf,
                                     offset=dateidxsize_bytes)

        if iscreate:
            self.dateiniidx[:] = -1
            self.dateendidx[:] = -1

    def malloc_symbolidx(self, shm_name):
        hashtblsize = int(self.table.records.size*5)
        hashtblsize_bytes = int(hashtblsize * 4)
        listsize = self.table.records.size
        listsize_bytes = int(listsize * 4)

        # symbol index
        iscreate = False
        [self.symbolidxshm, ismalloc] = self.shareddata.malloc(
            shm_name+'#symbolidx')
        if not ismalloc:
            [self.symbolidxshm, ismalloc] = self.shareddata.malloc(shm_name+'#symbolidx',
                                                                   create=True, size=int(hashtblsize_bytes+listsize_bytes))
            iscreate = True

        self.symbollastidx = np.ndarray(
            (hashtblsize,), dtype=np.int32, buffer=self.symbolidxshm.buf)
        self.symbolprevidx = np.ndarray((listsize,), dtype=np.int32, buffer=self.symbolidxshm.buf,
                                        offset=hashtblsize_bytes)

        if iscreate:
            self.symbollastidx[:] = -1
            self.symbolprevidx[:] = -1

    def malloc_portfolioidx(self, shm_name):
        hashtblsize = int(self.table.records.size*5)
        hashtblsize_bytes = int(hashtblsize * 4)
        listsize = self.table.records.size
        listsize_bytes = int(listsize * 4)

        # portfolio index
        iscreate = False
        [self.portidxshm, ismalloc] = self.shareddata.malloc(
            shm_name+'#portidx')
        if not ismalloc:
            [self.portidxshm, ismalloc] = self.shareddata.malloc(shm_name+'#portidx',
                                                                 create=True, size=int(hashtblsize_bytes+listsize_bytes))
            iscreate = True

        self.portlastidx = np.ndarray(
            (hashtblsize,), dtype=np.int32, buffer=self.portidxshm.buf)
        self.portprevidx = np.ndarray((listsize,), dtype=np.int32, buffer=self.portidxshm.buf,
                                      offset=hashtblsize_bytes)

        if iscreate:
            self.portlastidx[:] = -1
            self.portprevidx[:] = -1

    def malloc_dateportfolioidx(self, shm_name):
        portlistsize = int(self.table.records.size*2)
        keysize = int(self.table.records.size*5)
        keysize_bytes = int(keysize * 4)
        portidxsize_bytes = 4 + int(keysize_bytes*2) + int(portlistsize*4)

        iscreate = False
        [self.dtportidxshm, ismalloc] = self.shareddata.malloc(
            shm_name+'#dtportidx')
        if not ismalloc:
            [self.dtportidxshm, ismalloc] = self.shareddata.malloc(
                shm_name+'#dtportidx', create=True, size=portidxsize_bytes)
            iscreate = True

        self.portlistcount = np.ndarray(
            (1,), dtype=np.int32, buffer=self.dtportidxshm.buf)[0]
        self.portiniidx = np.ndarray((keysize,), dtype=np.int32,
                                     buffer=self.dtportidxshm.buf, offset=4)
        self.portendidx = np.ndarray((keysize,), dtype=np.int32,
                                     buffer=self.dtportidxshm.buf, offset=int(4+keysize_bytes))
        self.portlist = np.ndarray((portlistsize,), dtype=np.int32,
                                   buffer=self.dtportidxshm.buf, offset=int(4+keysize_bytes*2))

        if iscreate:
            self.portlistcount = 0
            self.portiniidx[:] = -1
            self.portendidx[:] = -1
            self.portlist[:] = -1

    def create_index(self):
        ti = time.time()
        if self.table.records.count > 0:
            print('Creating index %s %i lines...' %
                  (self.table.relpath, self.table.records.count))
            time.sleep(0.001)
            self.pkey[:] = -1
            self.dateiniidx[:] = -1
            self.dateendidx[:] = -1
            arr = self.table.records
            if 'date_portfolio_' in self.pkeystr:
                self.portlistcount = 0
                self.portiniidx[:] = -1
                self.portendidx[:] = -1
                self.portlist[:] = -1
                success = self.create_index_func(arr, self.table.records.count,
                                                 self.pkey, self.dateiniidx, self.dateendidx, self.dateunit,
                                                 self.portiniidx, self.portendidx, self.portlist, self.portlistcount, 0)
                self.portlistcount = self.table.records.count
            elif 'date_symbol' == self.pkeystr:
                self.symbollastidx[:] = -1
                self.symbolprevidx[:] = -1
                success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                                 self.dateiniidx, self.dateendidx, self.dateunit, self.symbollastidx, self.symbolprevidx, 0)
            elif 'date_portfolio' == self.pkeystr:
                self.portlastidx[:] = -1
                self.portprevidx[:] = -1
                success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                                 self.dateiniidx, self.dateendidx, self.dateunit, self.portlastidx, self.portprevidx, 0)
            else:
                success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                                 self.dateiniidx, self.dateendidx, self.dateunit, 0)

            if not success:
                Logger.log.critical('Duplicated Index %s!!!' %
                                    self.table.relpath)
                raise Exception('Duplicated Index %s!!!' % self.table.relpath)

            print('Creating index %s %i lines/s DONE!' %
                  (self.table.relpath, self.table.records.count/(time.time()-ti)))

    def update_index(self, start):
        ti = time.time()
        Logger.log.info('Updating index %s %i lines...' %
              (self.table.relpath, self.table.records.count))
        time.sleep(0.001)
        self.pkey[:] = -1
        self.dateiniidx[:] = -1
        self.dateendidx[:] = -1
        arr = self.table.records[0:self.table.records.size]
        if 'date_portfolio_' in self.pkeystr:
            self.portlistcount = 0
            self.portiniidx[:] = -1
            self.portendidx[:] = -1
            self.portlist[:] = -1
            success = self.create_index_func(arr, self.table.records.count,
                                             self.pkey, self.dateiniidx, self.dateendidx, self.dateunit,
                                             self.portiniidx, self.portendidx, self.portlist, self.portlistcount, 0)
            self.portlistcount = self.table.records.count
        elif 'date_symbol' == self.pkeystr:
            self.symbollastidx[:] = -1
            self.symbolprevidx[:] = -1
            success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                             self.dateiniidx, self.dateendidx, self.dateunit, self.symbollastidx, self.symbolprevidx, 0)
        elif 'date_portfolio' == self.pkeystr:
            self.portlastidx[:] = -1
            self.portprevidx[:] = -1
            success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                             self.dateiniidx, self.dateendidx, self.dateunit, self.portlastidx, self.portprevidx, 0)
        else:
            success = self.create_index_func(arr, self.table.records.count, self.pkey,
                                             self.dateiniidx, self.dateendidx, self.dateunit, 0)
        if not success:
            Logger.log.critical('Duplicated Index %s!!!' % self.table.relpath)
            raise Exception('Duplicated Index %s!!!' % self.table.relpath)

        Logger.log.info('Updating index %s %i lines/s DONE!' %
              (self.table.relpath, self.table.records.count/(time.time()-ti)))

    def sort_index(self, shnumpy, start=0):
        
        try:
            self.table.acquire()
            
            keys = tuple(shnumpy[column][start:]
                         for column in self.pkeycolumns[::-1])
            idx = np.lexsort(keys)

            shift_idx = np.roll(idx, 1)
            if len(shift_idx) > 0:
                shift_idx[0] = -1
                idx_diff = idx - shift_idx
                unsortered_idx = np.where(idx_diff != 1)[0]
                if np.where(idx_diff != 1)[0].any():
                    _minchgid = np.min(unsortered_idx) + start
                    shnumpy.minchgid = _minchgid
                    shnumpy[start:] = shnumpy[start:][idx]                    
                    self.update_index(_minchgid)

        except Exception as e:
            Logger.log.error('Error sorting index!\n%s' % (e))
        finally:
            self.table.release()

    @staticmethod
    def get_pkeycolumns(database):
        if database == 'MarketData':
            return ['date', 'symbol']

        elif database == 'Relationships':
            return ['date', 'symbol1', 'symbol2']

        elif database == 'Portfolios':
            return ['date', 'portfolio']

        elif database == 'Signals':
            return ['date', 'portfolio', 'symbol']

        elif database == 'Risk':
            return ['date', 'portfolio', 'symbol']

        elif database == 'Positions':
            return ['date', 'portfolio', 'symbol']

        elif database == 'Orders':
            return ['date', 'portfolio', 'symbol', 'clordid']

        elif database == 'Trades':
            return ['date', 'portfolio', 'symbol', 'tradeid']

        else:
            raise Exception('Database not implemented!')
