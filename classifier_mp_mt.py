# minecraft import
import anvil

# Multiprocessing
import ctypes
import itertools
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from contextlib import contextmanager, closing

# For array manipulations
import numpy as np

# Own imports
from block_tests import get_type

class ClassifierMPMT:

    def __init__(self):
        self.blocks_chunk_x = 16
        self.blocks_chunk_y = 256
        self.blocks_chunk_z = 16
        self.max_chunk_x = 32
        self.max_chunk_z = 32

        self.size_x = self.max_chunk_x * self.blocks_chunk_x
        self.size_y = self.blocks_chunk_y
        self.size_z = self.max_chunk_z * self.blocks_chunk_z

    def init_shared(self, ncell):
        '''Create shared value array for processing.'''
        shared_array_base = mp.Array(ctypes.c_int, ncell, lock=False)
        return(shared_array_base)

    def tonumpyarray(self, shared_array):
        '''Create numpy array from shared memory.'''
        nparray = np.frombuffer(shared_array, dtype = ctypes.c_int)
        assert nparray.base is shared_array
        return nparray

    def init_worker(self, shared_array_, region_):
        '''Initialize worker for processing.

        Args:
            shared_array_: Object returned by init_shared
        '''
        global shared_np_array
        global region

        shared_np_array = self.tonumpyarray(shared_array_)
        region = region_

    def worker_fun(self, ix):
        '''Function to be run inside each worker'''
        shared_np_array.shape = (self.size_x, self.size_y, self.size_z)
        chunkX, chunkZ = ix

        try:
            chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
        except:
            print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

        if chunk:
            self.classify(chunk, chunkX, chunkZ)

    def classify(self, chunk, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0
        blocks_chunk_x = 16
        blocks_chunk_z = 16
        for block in chunk.stream_chunk():
            shared_np_array[x + blocks_chunk_x * chunk_x, y, z + blocks_chunk_z * chunk_z] = get_type(block.id)

            # TODO self.blocks_chunk_x
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

    def classify_all_mp(self, region):
        shared_array = self.init_shared(self.size_x * self.size_y * self.size_z)

        window_idxs = [(i, j) for i, j in
                    itertools.product(range(0, self.max_chunk_x),
                                        range(0, self.max_chunk_z))]

        with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (shared_array, region))) as pool:
            res = pool.map(self.worker_fun, window_idxs)

        pool.close()
        pool.join()

        self.classified_region = self.tonumpyarray(shared_array)
        self.classified_region.shape = (self.size_x, self.size_y, self.size_z)

# https://stackoverflow.com/questions/3033952/threading-pool-similar-to-the-multiprocessing-pool
    def classify_all_mt(self, region):
        shared_array = self.init_shared(self.size_x * self.size_y * self.size_z)

        window_idxs = [(i, j) for i, j in
                    itertools.product(range(0, self.max_chunk_x),
                                        range(0, self.max_chunk_z))]

        with closing(ThreadPool(processes=4, initializer = self.init_worker, initargs = (shared_array, region))) as pool:
            res = pool.map(self.worker_fun, window_idxs)

        pool.close()
        pool.join()

        self.classified_region = self.tonumpyarray(shared_array)
        self.classified_region.shape = (self.size_x, self.size_y, self.size_z)
