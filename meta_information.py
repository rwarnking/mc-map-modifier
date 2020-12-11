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
        self.algo_step = 0
        self.algo_step_max = cfg.A_FINISHED

        self.counts = Counts()

        self.file_count = 0
        self.file_count_max = 1

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

        self.start_ms = 0
        self.end_ms = 0
        self.elapsed_time = 0
        self.estimated_time = 0
        self.t_per_chunk = 0.5

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

    def update_estimated_time(self):
        t_c = cfg.T_CLASSIFY * (0 if (self.algo_step > cfg.A_CLASSIFY) else 1)
        t_i = cfg.T_IDENTIFY * (0 if (self.algo_step > cfg.A_IDENTIFY) else 1)
        t_s = cfg.T_SAVE * (0 if (self.algo_step > cfg.A_SAVE) else 1)

        chunks = self.counts.chunks.value if self.algo_step >= cfg.A_MODIFY else 0
        t_m = ((self.counts.chunk_max - chunks) \
            + (self.file_count_max - self.file_count - 1) * self.counts.chunk_max) * self.t_per_chunk

        self.estimated_time = (t_c + t_i + t_s) * (self.file_count_max - self.file_count) + t_m

    def start_time(self):
        self.start_ms = int(round(time.time() * 1000))

    def end_time(self):
        self.end_ms = int(round(time.time() * 1000))

    def update_elapsed(self):
        self.elapsed_time += (self.end_ms - self.start_ms) / 1000
        self.t_per_chunk = self.elapsed_time / (self.counts.chunk_max * self.file_count + self.counts.chunks.value)

class Counts():

    def __init__(self):
        self.algo_step = 0
        self.algo_step_max = cfg.A_FINISHED

        self.chunks = Value('i', 0)
        self.chunk_max = cfg.REGION_C_X * cfg.REGION_C_Z
        self.label_max = Value('i', 0)
        self.file_count = 0
        self.file_count_max = 1

        self.changed_air = Value('i', 0)
        self.changed_water = Value('i', 0)
        self.changed_repl = Value('i', 0)
