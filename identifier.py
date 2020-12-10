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
        self.change_count_air = 0
        self.change_count_repl = 0

        # TODO
        self.mp_helper = MP_Helper()

    ###############################################################################################

    # TODO np.savetxt('data2.csv', arr[1], fmt='%i', delimiter=',')
    # TODO each array does add approx 20 secounds to the classify process
    # times
    # classify: 64048 - 86219
    # identify: 62331 - 74528
    # modify: 476081
    # save: 208582
    # total: 814072 upto 900000
    def identify(self, classified_air_region, classified_water_region, classified_repl_region, label_count, label_count_max):
        self.label_air_mp(classified_air_region, label_count, label_count_max)
        # TODO the problem is, that the blocks are first replaced with water but
        # afterwards replaced again due to the relacementtest
        # for smaller sizes this should be fixed by the tickness test, but for bigger pockets
        # it is recommended to first do the replace and afterwards do the waterblocks
        self.label_water(classified_water_region, label_count, label_count_max)
        self.label_repl(classified_repl_region, label_count, label_count_max)

        return [self.change_count_water, self.change_count_air, self.change_count_repl]

    ###############################################################################################

    def label_air_mp(self, classified_air_region, label_count, label_count_max):
        arr1, num1 = label2(classified_air_region, np.ones((3, 3, 3)))
        # TODO check for amount of label and then parallelise if needed
        # TODO unnecessary elements are tested: [i for i in range(1, 82, 20)] => [1, 21, 41, 61, 81]
        # 81 upto 101 are tested even if 82 is the max
        # TODO 20 as variable inside the process
        process_elem = 20

        label_count.value = 0
        label_count_max.value = num1 # last label count = 487

        identified_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)

        window_idxs = [i for i in range(1, num1 + 1, process_elem)]

        with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (identified_shared, classified_air_region, arr1, label_count))) as pool:
            res = pool.map(self.worker_fun, window_idxs)

        pool.close()
        pool.join()

        self.identified = self.mp_helper.tonumpyarray(identified_shared)
        self.identified.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)

    ###############################################################################################

    def label_water(self, classified_water_region, label_count, label_count_max):
        # TODO it seems like two blocks above each other are not correctly identified
        arr2, num2 = label(classified_water_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        label_count.value = 0
        label_count_max.value = num2 # last label count = 9

        for idx in range(1, num2 + 1):
            result = np.nonzero(arr2 == idx)
            lenght = len(result[0])

            if lenght <= self.wp_size:
                self.fill_array(self.identified, result, cfg.WATERBLOCK)
                self.change_count_water += lenght
            label_count.value += 1

    ###############################################################################################

    def label_repl(self, classified_repl_region, label_count, label_count_max):
        classified_repl_region = ndimage.binary_erosion(classified_repl_region, structure=np.ones((self.repl_area, self.repl_area, self.repl_area))).astype(classified_repl_region.dtype)
        arr3, num3 = label(classified_repl_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND)
        label_count.value = 0
        label_count_max.value = num3  # last label count = 16 for repl_area = 5

        for idx in range(1, num3 + 1):
            result = np.nonzero(arr3 == idx)
            lenght = len(result[0])

            # if self.repl_blocks == 1: # TODO
            self.fill_array(self.identified, result, cfg.SOLIDAREA)
            self.change_count_repl += lenght

            label_count.value += 1

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
    def init_worker(self, identified_shared_, classified_air_region_, arr1_, label_count_):
        '''Initialize worker for processing.

        Args:
            identified_shared_: ...
            classified_air_region_: ...
            arr1_: ...
        '''
        global identified_shared
        global classified_air_region
        global arr1
        global label_count

        identified_shared = self.mp_helper.tonumpyarray(identified_shared_)
        classified_air_region = classified_air_region_
        arr1 = arr1_
        label_count = label_count_

    # TODO rename
    def worker_fun(self, ix):
        '''Function to be run inside each worker'''
        identified_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        num = ix

        # TODO 20 variable
        for idx in range(num, num + 20):
            result = np.nonzero(arr1 == idx)
            lenght = len(result[0])

            if lenght <= self.apocket_size and self.check_all(classified_air_region, result, cfg.G_AIR):
                self.fill_array(identified_shared, result, cfg.AIRPOCKET)
                self.change_count_air += lenght

            label_count.value += 1