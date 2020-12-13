# For array manipulations
import numpy as np
from math import ceil

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
    # Labeling functions
    ###############################################################################################
    def label_air(self, identified_shared, classified_air_region, counts):
        labeled, num = label2(classified_air_region, np.ones((3, 3, 3)))
        counts.chunks.value = 0
        counts.label_max.value = num # last label count = 487

        # Check for label-amount and use multiprocessing if needed
        if num < cfg.PROCESSES * 5:
            validator = lambda l, r: l <= self.apocket_size and self.check_all(classified_air_region, r, cfg.G_AIR)
            self.fill_labels_sp(labeled, num, classified_air_region, cfg.AIRPOCKET, counts, counts.changed_air, validator)
        else:
            self.fill_labels_mp(labeled, num, classified_air_region, identified_shared, counts)

    def label_water(self, identified_shared, classified_water_region, counts):
        labeled, num = label(classified_water_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        counts.chunks.value = 0
        counts.label_max.value = num # last label count = 9

        validator = lambda l, r: l <= self.wp_size
        self.fill_labels_sp(labeled, num, classified_water_region, cfg.WATERBLOCK, counts, counts.changed_water, validator)

    def label_repl(self, identified_shared, classified_repl_region, counts):
        classified_repl_region = ndimage.binary_erosion(classified_repl_region, structure=np.ones((self.repl_area, self.repl_area, self.repl_area))).astype(classified_repl_region.dtype)
        labeled, num = label(classified_repl_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        counts.chunks.value = 0
        counts.label_max.value = num  # last label count = 16 for repl_area = 5

        validator = lambda l, r: True
        self.fill_labels_sp(labeled, num, classified_repl_region, cfg.SOLIDAREA, counts, counts.changed_repl, validator)

    ###############################################################################################
    # Filler functions
    ###############################################################################################
    def fill_labels_sp(self, labeled, num, region, fill, counts, changed, validator):
        for idx in range(1, num + 1):
            result = np.nonzero(labeled == idx)
            length = len(result[0])

            if validator(length, result):
                self.fill_array(self.identified, result, fill)
                changed.value += length

            counts.chunks.value += 1

    def fill_labels_mp(self, labeled, num, region, identified_shared, counts):
        upper_bound = int(ceil((num + 1) / cfg.PROCESSES) * cfg.PROCESSES)
        self.elems = int(upper_bound / cfg.PROCESSES)

        window_idxs = [i for i in range(1, upper_bound, self.elems)]

        with closing(mp.Pool(processes=cfg.PROCESSES, initializer = self.init_worker, initargs = (identified_shared, region, labeled, counts))) as pool:
            res = pool.map(self.worker_task, window_idxs)

        pool.close()
        pool.join()

    ###############################################################################################
    # Helper functions
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

        for idx in range(num, num + self.elems):
            result = np.nonzero(labeled == idx)
            length = len(result[0])

            if length <= self.apocket_size and self.check_all(c_region, result, cfg.G_AIR):
                self.fill_array(i_shared, result, cfg.AIRPOCKET)
                counts.changed_air.value += length

            counts.chunks.value += 1
