# Allows for udates inside the multiprocessing
from multiprocessing import Value

# TODO
# Timing
import time
import datetime
from time import gmtime, strftime

from tkinter import StringVar, IntVar
import queue

import config as cfg

class MetaInformation():

    def __init__(self):
        self.counts = Counts()
        self.timer = Timer()

        # TODO dont save these as tkinter objects but only set them at application start
        self.water_blocks = IntVar()
        self.air_pockets = IntVar()
        self.repl_blocks = IntVar()

        self.wpocket_size = StringVar()
        self.wpocket_size.set("2")
        self.apocket_size = StringVar()
        self.apocket_size.set("1")
        self.repl_area = StringVar()
        self.repl_area.set("2")

        self.text_queue = queue.Queue()

        self.finished = True

    # def set_file_progess(self, file_progress):
    #     self.file_progress = file_progress

    # def set_file_max(self, file_max):
    #     self.file_max = file_max

    def set_dirs(self, s_dir, r_dir, t_dir):
        self.source_dir = StringVar()
        self.source_dir.set(s_dir)

        self.replacement_dir = StringVar()
        self.replacement_dir.set(r_dir)

        self.target_dir = StringVar()
        self.target_dir.set(t_dir)

    def get_current_count(self):
        if self.counts.algo_step == cfg.A_CLASSIFY:
            return self.counts.chunks_c.value
        elif self.counts.algo_step == cfg.A_IDENTIFY:
            return self.counts.label_i.value
        elif self.counts.algo_step == cfg.A_MODIFY or self.counts.algo_step == cfg.A_SAVE or self.counts.algo_step == cfg.A_FINISHED:
            return self.counts.chunks_m.value
        else:
            # TODO
            print("This should not happen in metainfo")
            return 0

    def get_current_max_count(self):
        if self.counts.algo_step == cfg.A_CLASSIFY:
            return self.counts.chunk_c_max
        elif self.counts.algo_step == cfg.A_IDENTIFY:
            return self.counts.label_i_max.value
        elif self.counts.algo_step == cfg.A_MODIFY or self.counts.algo_step == cfg.A_SAVE or self.counts.algo_step == cfg.A_FINISHED:
            return self.counts.chunk_m_max
        else:
            # TODO
            print("This should not happen in metainfo")
            return 0

    def update_estimated_time(self):
        self.timer.update_estimated_time(
            self.counts,
            self.water_blocks.get() == 1 or self.air_pockets.get() == 1 or self.repl_blocks.get() == 1
        )

    def get_tunnel_start(self):
        return [175, 90, 250]

    def get_tunnel_end(self):
        return [400, 90, 250]

class Counts():

    def __init__(self):
        self.algo_step = 0
        self.algo_step_max = cfg.A_FINISHED

        self.file_count = 0
        self.file_count_max = 1

        self.chunks_c = Value('i', 0)
        self.label_i = Value('i', 0)
        self.chunks_m = Value('i', 0)
        self.chunk_c_max = cfg.REGION_C_X * cfg.REGION_C_Z
        self.label_i_max = Value('i', 500)
        self.chunk_m_max = cfg.REGION_C_X * cfg.REGION_C_Z

        self.changed_air = Value('i', 0)
        self.changed_water = Value('i', 0)
        self.changed_repl = Value('i', 0)

class Timer():

    def __init__(self):
        self.start_ms = 0
        self.end_ms = 0

        self.start2_ms = Value('i', 0)
        self.end2_ms = Value('i', 0)

        self.elapsed_c_time = Value('f', 0.0)
        self.elapsed_i_time = Value('f', 0.0)
        self.elapsed_m_time = 0
        # self.t_per_c_chunk = 0.1
        self.t_per_c_chunk = Value('f', 0.075)
        self.t_per_i_label = Value('f', 0.12)
        self.t_per_m_chunk = 0.5

        self.estimated_time = 0

    def update_estimated_time(self, counts, n_copy_only):
        remaining_files = counts.file_count_max - counts.file_count

        elems = counts.chunks_c.value if counts.algo_step >= cfg.A_CLASSIFY else 0
        t_c = ((counts.chunk_c_max - elems) \
            + (remaining_files - 1) * counts.chunk_c_max) * self.t_per_c_chunk.value

        elems = counts.label_i.value if counts.algo_step >= cfg.A_IDENTIFY else 0
        t_i = ((counts.label_i_max.value - elems) \
            + (remaining_files - 1) * counts.label_i_max.value) * self.t_per_i_label.value

        elems = counts.chunks_m.value if counts.algo_step >= cfg.A_MODIFY else 0
        t_m = ((counts.chunk_m_max - elems) \
            + (remaining_files - 1) * counts.chunk_m_max) * self.t_per_m_chunk

        t_s = cfg.T_SAVE * (0 if (counts.algo_step > cfg.A_SAVE) else 1) * remaining_files

        if n_copy_only:
            self.estimated_time = t_c + t_i + t_m + t_s
        else:
            self.estimated_time = t_m + t_s

    def start_time(self):
        self.start_ms = int(round(time.time() * 1000))

    def end_time(self):
        self.end_ms = int(round(time.time() * 1000))

    def start2_time(self):
        self.start2_ms.value = int(round(time.time() * 1000))

    def end2_time(self):
        self.end2_ms.value = int(round(time.time() * 1000))

    def update_c_elapsed(self, counts):
        self.elapsed_c_time.value += (self.end2_ms.value - self.start2_ms.value) / 1000
        self.t_per_c_chunk.value = self.elapsed_c_time.value / (counts.chunk_c_max * counts.file_count + counts.chunks_c.value)

    def update_i_elapsed(self, counts):
        self.elapsed_i_time.value += (self.end2_ms.value - self.start2_ms.value) / 1000
        self.t_per_i_label.value = self.elapsed_i_time.value / (counts.label_i_max.value * counts.file_count + counts.label_i.value)

    def update_m_elapsed(self, counts):
        self.elapsed_m_time += (self.end_ms - self.start_ms) / 1000
        self.t_per_m_chunk = self.elapsed_m_time / (counts.chunk_m_max * counts.file_count + counts.chunks_m.value)
