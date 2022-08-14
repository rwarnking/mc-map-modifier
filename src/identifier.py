# Multiprocessing
import multiprocessing as mp
from contextlib import closing
from math import ceil

import config as cfg  # Own import
import numpy as np
from mp_helper import MP_Helper  # Own import

# Image processing
# TODO rename and merge import
from scipy import ndimage
from scipy.ndimage import label as label2
from skimage.measure import label


class Identifier:
    def __init__(self, meta_info):
        # self.meta_info = meta_info

        self.wp_size = int(meta_info.wpocket_size.get())
        self.apocket_size = int(meta_info.apocket_size.get())
        self.repl_area = int(meta_info.repl_area.get()) * 2 + 1

        self.air_pockets = meta_info.air_pockets.get()
        self.water_blocks = meta_info.water_blocks.get()
        self.repl_blocks = meta_info.repl_blocks.get()
        self.add_tunnel = meta_info.add_tunnel.get()

        self.change_count_water = 0
        self.change_count_repl = 0

        # TODO
        self.mp_helper = MP_Helper()

    ###############################################################################################

    def identify(self, c_regions, counts, timer):
        identified_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)

        self.identified = self.mp_helper.tonumpyarray(identified_shared)
        self.identified.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)

        if self.air_pockets == 1:
            self.label_air(identified_shared, c_regions[cfg.C_A_AIR], counts, timer)
        if self.repl_blocks == 1:
            self.label_repl(identified_shared, c_regions[cfg.C_A_REPL], counts, timer)
        # Do the water replacement after the block replacement to prevent changes of
        # water pockets due to replacement
        if self.water_blocks == 1:
            self.label_water(identified_shared, c_regions[cfg.C_A_WATER], counts, timer)

    ###############################################################################################
    # Labeling functions
    ###############################################################################################
    def label_air(self, identified_shared, c_region, counts, timer):
        # TODO make labeled and num self?
        labeled, num = label2(c_region, np.ones((3, 3, 3)))
        labeled = labeled.astype(np.int32)
        counts.label_i.value = 0
        counts.label_i_max.value = num

        self.filler = cfg.AIRPOCKET

        # Check for label-amount and use multiprocessing if needed
        if num <= 0:
            return
        elif num < cfg.PROCESSES * 5:
            valid = self.validator_air
            self.fill_labels_sp(
                self.identified, labeled, c_region, counts, counts.changed_air, valid, timer, num
            )
        else:
            self.fill_labels_mp(
                identified_shared, labeled, c_region, counts, counts.changed_air, 1, timer, num
            )

    def label_water(self, identified_shared, c_region, counts, timer):
        labeled, num = label(
            c_region, connectivity=3, return_num=True, background=cfg.G_BACKGROUND
        )
        labeled = labeled.astype(np.int32)
        counts.label_i.value = 0
        counts.label_i_max.value = num

        self.filler = cfg.WATERBLOCK

        if num <= 0:
            return
        elif num < cfg.PROCESSES * 5:
            valid = self.validator_water
            self.fill_labels_sp(
                self.identified, labeled, c_region, counts, counts.changed_water, valid, timer, num
            )
        else:
            self.fill_labels_mp(
                identified_shared, labeled, c_region, counts, counts.changed_water, 2, timer, num
            )

    def label_repl(self, identified_shared, c_region, counts, timer):
        """
        Args:
            identified_shared: ...
            c_region: ...
            counts: ...
        """
        if self.repl_area > 0:
            c_region = ndimage.binary_erosion(
                c_region, structure=np.ones((self.repl_area, self.repl_area, self.repl_area))
            ).astype(np.int32)
        labeled, num = label(
            c_region, connectivity=2, return_num=True, background=cfg.G_BACKGROUND
        )
        labeled = labeled.astype(np.int32)
        counts.label_i.value = 0
        counts.label_i_max.value = num

        self.filler = cfg.SOLIDAREA

        if num <= 0:
            return
        elif num < cfg.PROCESSES * 5:
            valid = self.validator_repl
            self.fill_labels_sp(
                self.identified, labeled, c_region, counts, counts.changed_repl, valid, timer, num
            )
        else:
            self.fill_labels_mp(
                identified_shared, labeled, c_region, counts, counts.changed_repl, 3, timer, num
            )

    ###############################################################################################
    # Filler functions
    ###############################################################################################
    # TODO the region is only used inside the validator, use self.region?
    def fill_labels_sp(
        self, i_array, l_array, c_array, counts, changed, validator, timer, end, begin=1
    ):
        timer.start2_time()
        for idx in range(begin, end + 1):
            result = np.nonzero(l_array == idx)
            length = len(result[0])

            if validator(length, result):
                self.fill_array(i_array, result, self.filler)
                changed.value += length

            counts.label_i.value += 1
        timer.end2_time()
        timer.update_i_elapsed(counts)

    def fill_labels_mp(
        self, identified_shared, labeled, c_region, counts, changed, v_idx, timer, num
    ):
        labeled_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)
        self.mp_helper.fill_shared(
            labeled_shared, labeled, (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        )
        classified_shared = self.mp_helper.init_shared(cfg.REGION_B_TOTAL)
        self.mp_helper.fill_shared(
            classified_shared, c_region, (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        )

        upper_bound = int(ceil((num + 1) / cfg.PROCESSES) * cfg.PROCESSES)
        self.elems = int(upper_bound / cfg.PROCESSES)

        window_idxs = [i for i in range(1, upper_bound, self.elems)]

        with closing(
            mp.Pool(
                processes=cfg.PROCESSES,
                initializer=self.init_worker,
                initargs=(
                    identified_shared,
                    labeled_shared,
                    classified_shared,
                    counts,
                    changed,
                    v_idx,
                    timer,
                ),
            )
        ) as pool:
            pool.map(self.worker_task, window_idxs)

        pool.close()
        pool.join()

    ###############################################################################################
    # Multiprocessing functions
    ###############################################################################################
    # TODO combine with classifier mp
    # TODO clean this up a little bit by using a list?
    def init_worker(self, i_shared_, l_shared_, c_shared_, counts_, changed_, v_idx_, timer_):
        """Initialize worker for processing.

        Args:
            i_shared_: ...
            c_region: ...
            labeled_: ...
        """
        global i_shared
        global l_shared
        global c_shared
        global counts
        global changed
        global validator
        global timer

        i_shared = self.mp_helper.tonumpyarray(i_shared_)
        l_shared = self.mp_helper.tonumpyarray(l_shared_)
        c_shared = self.mp_helper.tonumpyarray(c_shared_)
        counts = counts_
        changed = changed_
        timer = timer_

        if v_idx_ == 1:
            validator = self.validator_air
        elif v_idx_ == 2:
            validator = self.validator_water
        else:
            validator = self.validator_repl

    def validator_air(self, length, arr):
        return length <= self.apocket_size and self.check_all(c_shared, arr, cfg.G_AIR)

    def validator_water(self, length, arr):
        return length <= self.wp_size

    def validator_repl(self, length, arr):
        return True

    def worker_task(self, ix):
        """Function to be run inside each worker"""
        i_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        l_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        c_shared.shape = (cfg.REGION_B_X, cfg.REGION_B_Y, cfg.REGION_B_Z)
        num = ix

        self.fill_labels_sp(
            i_shared, l_shared, c_shared, counts, changed, validator, timer, num + self.elems, num
        )

    ###############################################################################################
    # Helper functions
    ###############################################################################################
    # TODO is there a numpy function for this?
    def fill_array(self, arr, result, value):
        arr[result[0], result[1], result[2]] = value

    # TODO can this be done better?
    def check_all(self, array, result, value):
        """
        Returns false if there is a value in the
        array that is not equal to the value-parameter.
        """
        list_of_indices = list(zip(result[0], result[1], result[2]))

        for xyz in list_of_indices:
            x, y, z = xyz
            if array[x, y, z] != value:
                return False
        return True
