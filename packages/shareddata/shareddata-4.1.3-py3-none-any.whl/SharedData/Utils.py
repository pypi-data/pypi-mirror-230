import os
from multiprocessing import resource_tracker


def remove_shm_from_resource_tracker():
    """Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

    More details at: https://bugs.python.org/issue38119
    """

    def fix_register(name, rtype):
        return
    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        return
    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]


if os.name == 'posix':
    from cffi import FFI
    # atomic semaphore operation
    ffi = FFI()
    ffi.cdef("""
    unsigned char bool_compare_and_swap(long , long, unsigned char, unsigned char);
    unsigned char long_compare_and_swap(long , long, long, long);
    """)
    cpp = ffi.verify("""
    unsigned char bool_compare_and_swap(long mem_addr, long seek, unsigned char old, unsigned char new) {
        unsigned char * mem_ptr = (unsigned char *) mem_addr;
        mem_ptr += seek;
        return __sync_bool_compare_and_swap(mem_ptr, old, new);
    };
    unsigned char long_compare_and_swap(long mem_addr, long seek, long old, long new) {
        unsigned char * mem_ptr = (unsigned char *) mem_addr;
        mem_ptr += seek;
        return __sync_bool_compare_and_swap(mem_ptr, old, new);
    };
    """)
