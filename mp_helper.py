import numpy as np

# Multiprocessing
import ctypes
import multiprocessing as mp

class MP_Helper:

    def init_shared(self, ncell):
        '''Create shared value array for processing.'''
        shared_array_base = mp.Array(ctypes.c_int, ncell, lock=False)
        return(shared_array_base)

    def tonumpyarray(self, shared_array):
        '''Create numpy array from shared memory.'''
        nparray = np.frombuffer(shared_array, dtype = ctypes.c_int)
        assert nparray.base is shared_array
        return nparray
