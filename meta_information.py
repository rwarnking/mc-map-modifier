from tkinter import StringVar, IntVar
import queue

class MetaInformation():

    def __init__(self):

        self.chunk_count = 0
        self.file_count = 0
        self.chunk_count_max = 0
        self.file_count_max = 0

        self.water_blocks = IntVar()
        self.air_pockets = IntVar()
        self.repl_blocks = IntVar()

        self.text_queue = queue.Queue()
        self.elapsed_time = 0
        self.estimated_time = 0

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

