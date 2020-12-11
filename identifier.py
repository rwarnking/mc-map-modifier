# For array manipulations
import numpy as np

# Multiprocessing
import multiprocessing as mp
from contextlib import closing

# Image processing
# TODO rename and merge import
from scipy.ndimage import label as label2
from scipy import ndimage
from skimage.measure import label

# Own import
from mp_helper import MP_Helper
import config as cfg

class Identifier:

    def __init__(self, meta_info):
        # self.meta_info = meta_info

        self.wp_size = int(meta_info.wpocket_size.get())
        self.apocket_size = int(meta_info.apocket_size.get())
        self.repl_area = int(meta_info.repl_area.get()) * 2 + 1

        self.water_blocks = meta_info.water_blocks.get()
        self.air_pockets = meta_info.air_pockets.get()
        self.repl_blocks = meta_info.repl_blocks.get()

        self.change_count_water = 0
        self.change_count_repl = 0

        # TODO
        self.mp_helper = MP_Helper()

    ###############################################################################################

    # TODO np.savetxt('data2.csv', arr[1], fmt='%i', delimiter=',')
    # times
    # classify: 64048 - 86219
    # identify: 62331 - 74528
    # modify: 476081
    # save: 208582
    # total: 814072 upto 900000
    def identify(self, classified_air_region, classified_water_region, classified_repl_region, counts):
        identified_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)

        self.identified = self.mp_helper.tonumpyarray(identified_shared)
        self.identified.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)

        self.label_air(identified_shared, classified_air_region, counts)
        self.label_repl(identified_shared, classified_repl_region, counts)
        # Do the water replacement after the block replacement to prevent changes of
        # water pockets due to replacement
        self.label_water(identified_shared, classified_water_region, counts)

    ###############################################################################################

    def label_air(self, identified_shared, classified_air_region, counts):
        arr1, num1 = label2(classified_air_region, np.ones((3, 3, 3)))
        counts.chunks.value = 0
        counts.label_max.value = num1 # last label count = 487

        # Check for label-amount and use multiprocessing if needed
        if num1 < cfg.I_PROCESS_ELEM * 2:
            for idx in range(num1 + 1):
                result = np.nonzero(arr1 == idx)
                length = len(result[0])

                if length <= self.apocket_size and self.check_all(classified_air_region, result, cfg.G_AIR):
                    self.fill_array(self.identified, result, cfg.AIRPOCKET)
                    counts.changed_air.value += length

                counts.chunks.value += 1
        else:
            # TODO unnecessary elements are tested: [i for i in range(1, 82, 20)] => [1, 21, 41, 61, 81]
            # 81 upto 101 are tested even if 82 is the max
            window_idxs = [i for i in range(1, num1 + 1, cfg.I_PROCESS_ELEM)]

            with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (identified_shared, classified_air_region, arr1, counts))) as pool:
                res = pool.map(self.worker_task, window_idxs)

            pool.close()
            pool.join()

    ###############################################################################################

    def label_water(self, identified_shared, classified_water_region, counts):
        # TODO it seems like two blocks above each other are not correctly identified
        arr2, num2 = label(classified_water_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        counts.chunks.value = 0
        counts.label_max.value = num2 # last label count = 9

        for idx in range(1, num2 + 1):
            result = np.nonzero(arr2 == idx)
            length = len(result[0])

            if length <= self.wp_size:
                self.fill_array(self.identified, result, cfg.WATERBLOCK)
                counts.changed_water.value += length
            counts.chunks.value += 1

    ###############################################################################################

    def label_repl(self, identified_shared, classified_repl_region, counts):
        classified_repl_region = ndimage.binary_erosion(classified_repl_region, structure=np.ones((self.repl_area, self.repl_area, self.repl_area))).astype(classified_repl_region.dtype)
        arr3, num3 = label(classified_repl_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        counts.chunks.value = 0
        counts.label_max.value = num3  # last label count = 16 for repl_area = 5

        for idx in range(1, num3 + 1):
            result = np.nonzero(arr3 == idx)
            length = len(result[0])

            # if self.repl_blocks == 1: # TODO
            self.fill_array(self.identified, result, cfg.SOLIDAREA)
            counts.changed_repl.value += length

            counts.chunks.value += 1

    ###############################################################################################

    # TODO is there a numpy function for this?
    def fill_array(self, arr, result, value):
        arr[result[0], result[1], result[2]] = value

    # TODO can this be done better?
    def check_all(self, array, result, value):
        '''Returns false if there is a value in the array that is not equal to the value-parameter.'''
        list_of_indices = list(zip(result[0], result[1], result[2]))

        for xyz in list_of_indices:
            x, y, z = xyz
            if array[x, y, z] != value:
                return False
        return True












    # TODO combine with classifier mp
    def init_worker(self, i_shared_, c_region_, labeled_, counts_):
        '''Initialize worker for processing.

        Args:
            i_shared_: ...
            c_region: ...
            labeled_: ...
        '''
        global i_shared
        global c_region
        global labeled
        global counts

        i_shared = self.mp_helper.tonumpyarray(i_shared_)
        c_region = c_region_
        labeled = labeled_
        counts = counts_

    def worker_task(self, ix):
        '''Function to be run inside each worker'''
        i_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        num = ix

        for idx in range(num, num + cfg.I_PROCESS_ELEM):
            result = np.nonzero(labeled == idx)
            length = len(result[0])

            if length <= self.apocket_size and self.check_all(c_region, result, cfg.G_AIR):
                self.fill_array(i_shared, result, cfg.AIRPOCKET)
                counts.changed_air.value += length

            counts.chunks.value += 1
