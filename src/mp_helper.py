# Multiprocessing
import ctypes
import multiprocessing as mp

import numpy as np


class MP_Helper:
    def init_shared(self, ncell):
        """Create shared value array for processing."""
        shared_array_base = mp.Array(ctypes.c_int, ncell, lock=False)
        return shared_array_base

    def fill_shared(self, _shared, fill, shape):
        """Fill shared array for."""
        X_np = np.frombuffer(_shared, dtype=np.int32)
        X_np.shape = shape
        np.copyto(X_np, fill)

    def tonumpyarray(self, shared_array):
        """Create numpy array from shared memory."""
        nparray = np.frombuffer(shared_array, dtype=ctypes.c_int)
        assert nparray.base is shared_array
        return nparray
