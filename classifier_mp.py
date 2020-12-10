# minecraft import
import anvil

# Multiprocessing
import itertools
import multiprocessing as mp
from contextlib import closing

# For array manipulations
import numpy as np

# Own imports
from block_tests import get_air_type, get_water_type, get_repl_type
from mp_helper import MP_Helper
import config as cfg

class ClassifierMP:

    def __init__(self, meta_info):
        # TODO dublicate with identifier
        self.mp_helper = MP_Helper()

    def classify_all_mp(self, region, chunk_count):
        air_array_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)
        water_array_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)
        repl_array_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)

        window_idxs = [(i, j) for i, j in
                    itertools.product(range(0, cfg.REGION_C_X),
                                        range(0, cfg.REGION_C_Z))]

        with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (air_array_shared, water_array_shared, repl_array_shared, region, chunk_count))) as pool:
            res = pool.map(self.worker_fun, window_idxs)

        pool.close()
        pool.join()

        self.classified_air_region = self.mp_helper.tonumpyarray(air_array_shared)
        self.classified_air_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        self.classified_water_region = self.mp_helper.tonumpyarray(water_array_shared)
        self.classified_water_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        self.classified_repl_region = self.mp_helper.tonumpyarray(repl_array_shared)
        self.classified_repl_region.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)

    def init_worker(self, air_array_shared_, water_array_shared_, repl_array_shared_, region_, chunk_count_):
        '''Initialize worker for processing.

        Args:
            shared_array_: Object returned by init_shared
        '''
        global air_array_shared
        global water_array_shared
        global repl_array_shared
        global region
        global chunk_count

        air_array_shared = self.mp_helper.tonumpyarray(air_array_shared_)
        water_array_shared = self.mp_helper.tonumpyarray(water_array_shared_)
        repl_array_shared = self.mp_helper.tonumpyarray(repl_array_shared_)
        region = region_
        chunk_count = chunk_count_

    # TODO rename
    def worker_fun(self, ix):
        '''Function to be run inside each worker'''
        air_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        water_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        repl_array_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        chunk_x, chunk_z = ix

        chunk_count.value += 1

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
