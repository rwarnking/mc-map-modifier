# Multiprocessing
import itertools
import multiprocessing as mp
from contextlib import closing

# minecraft import
import anvil
import config as cfg

# Own imports
from block_tests import get_air_type, get_repl_type, get_water_type
from mp_helper import MP_Helper


class ClassifierMP:
    def __init__(self, meta_info):
        # TODO dublicate with identifier
        self.mp_helper = MP_Helper()
        self.c_regions = [None] * cfg.C_A_COUNT

    def classify_all_mp(self, region, counts, timer):

        # Create a list of shared arrays that have the specified size
        shared_arrays = [
            self.mp_helper.init_shared(cfg.REGION_B_TOTAL) for x in range(cfg.C_A_COUNT)
        ]

        # Create pairs to index the different chunks -> (0, 0) (0, 1) (0, m) (1, 0) (2, 0) (n, m)
        window_idxs = [
            (i, j)
            for i, j in itertools.product(range(0, cfg.REGION_C_X), range(0, cfg.REGION_C_Z))
        ]

        with closing(
            mp.Pool(
                processes=cfg.PROCESSES,
                initializer=self.init_worker,
                initargs=(shared_arrays, region, counts, timer),
            )
        ) as pool:
            pool.map(self.worker_task, window_idxs)

        pool.close()
        pool.join()

        for idx in range(cfg.C_A_COUNT):
            self.c_regions[idx] = self.mp_helper.tonumpyarray(shared_arrays[idx])
            self.c_regions[idx].shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)

    def init_worker(self, shared_arrays_, region_, counts_, timer_):
        """Initialize worker for processing.

        Args:
            shared_array_: Object returned by init_shared
        """
        global shared_arrays
        global region
        global counts
        global timer

        shared_arrays = [self.mp_helper.tonumpyarray(array) for array in shared_arrays_]
        region = region_
        counts = counts_
        timer = timer_

    def worker_task(self, ix):
        """Function to be run inside each worker"""
        timer.start2_time()

        for array in shared_arrays:
            array.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        chunk_x, chunk_z = ix

        counts.chunks_c.value += 1

        try:
            chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
        except Exception:
            print(f"skipped non-existent chunk ({chunk_x},{chunk_z})")

        if chunk:
            self.classify(chunk, chunk_x, chunk_z)

        timer.end2_time()
        timer.update_c_elapsed(counts)

    def classify(self, chunk, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0
        chunk_b_x = cfg.CHUNK_B_X
        chunk_b_z = cfg.CHUNK_B_Z
        for block in chunk.stream_chunk():
            r_x = x + chunk_b_x * chunk_x
            r_z = z + chunk_b_z * chunk_z
            shared_arrays[cfg.C_A_AIR][r_x, y, r_z] = get_air_type(block.id)
            shared_arrays[cfg.C_A_WATER][r_x, y, r_z] = get_water_type(block.id)
            shared_arrays[cfg.C_A_REPL][r_x, y, r_z] = get_repl_type(block.id)

            if x == (cfg.CHUNK_B_X - 1) and z == (cfg.CHUNK_B_Z - 1):
                y += 1
            if x == (cfg.CHUNK_B_X - 1):
                z = (z + 1) % cfg.CHUNK_B_Z
            x = (x + 1) % cfg.CHUNK_B_X
