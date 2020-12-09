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
from block_tests import get_repl_type, get_air_type, get_water_type # TODO
import config as cfg

class ClassifierMPMT:

    def __init__(self):
        self.jo = 0 # TODO delete

    def init_shared(self, ncell):
        '''Create shared value array for processing.'''
        shared_array_base = mp.Array(ctypes.c_int, ncell, lock=False)
        return(shared_array_base)

    def tonumpyarray(self, shared_array):
        '''Create numpy array from shared memory.'''
        nparray = np.frombuffer(shared_array, dtype = ctypes.c_int)
        assert nparray.base is shared_array
        return nparray

    def init_worker(self, air_array_shared_, water_array_shared_, repl_array_shared_, region_):
        '''Initialize worker for processing.

        Args:
            shared_array_: Object returned by init_shared
        '''
        global air_array_shared
        global water_array_shared
        global repl_array_shared
        global region

        air_array_shared = self.tonumpyarray(air_array_shared_)
        water_array_shared = self.tonumpyarray(water_array_shared_)
        repl_array_shared = self.tonumpyarray(repl_array_shared_)
        region = region_

    # TODO rename
    def worker_fun(self, ix):
        '''Function to be run inside each worker'''
        air_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        water_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        repl_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        chunk_x, chunk_z = ix

        try:
            chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
        except:
            print(f'skipped non-existent chunk ({chunk_x},{chunk_z})')

        if chunk:
            self.classify(chunk, chunk_x, chunk_z)

    def classify(self, chunk, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0
        chunk_b_x = cfg.CHUNK_B_X
        chunk_b_z = cfg.CHUNK_B_Z
        for block in chunk.stream_chunk():
            r_x = x + chunk_b_x * chunk_x
            r_z = z + chunk_b_z * chunk_z
            air_array_shared[r_x, y, r_z] = get_air_type(block.id)
            water_array_shared[r_x, y, r_z] = get_water_type(block.id)
            repl_array_shared[r_x, y, r_z] = get_repl_type(block.id)

            # TODO chunk_b_x
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

    def classify_all_mp(self, region):
        # TODO calc once and dont do it again
        air_array_shared = self.init_shared(cfg.REGION_B_TOTAL)
        water_array_shared = self.init_shared(cfg.REGION_B_TOTAL)
        repl_array_shared = self.init_shared(cfg.REGION_B_TOTAL)

        window_idxs = [(i, j) for i, j in
                    itertools.product(range(0, cfg.REGION_C_X),
                                        range(0, cfg.REGION_C_Z))]

        with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (air_array_shared, water_array_shared, repl_array_shared, region))) as pool:
            res = pool.map(self.worker_fun, window_idxs)

        pool.close()
        pool.join()

        self.classified_air_region = self.tonumpyarray(air_array_shared)
        self.classified_air_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        self.classified_water_region = self.tonumpyarray(water_array_shared)
        self.classified_water_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        self.classified_repl_region = self.tonumpyarray(repl_array_shared)
        self.classified_repl_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
