from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *

import math
import queue
import threading

# Needed for the username
import os

# own imports
from modifier import run
from modifier import runloop
from meta_information import MetaInformation

PAD_X = 20
PAD_Y = (10, 0)

# Test path
S_DIR = "C:/Users/"+os.getlogin()+"/Projekte/mc-map-modifier/original"
#S_DIR = "C:/Users/"+os.getlogin()+"/AppData/Roaming/.minecraft/saves"
#R_DIR = "C:/Users/"+os.getlogin()+"/AppData/Roaming/.minecraft/saves"

class MainApp():

    def __init__(self, window):

        self.meta_info = MetaInformation()

        self.init_resource_folder(window)
        self.init_checkbuttons(window)
        self.init_progressindicator(window)
        self.init_details(window)

        self.run_button = Button(window, text="Dew it", command=lambda: self.run(window))
        self.run_button.grid(row=14, column=0, padx = PAD_X, pady = 10)

    def run(self, window):
        if not self.meta_info.finished:
            messagebox.showinfo(message="Modification is already happening.", title = "Error")
            window.after(50, lambda: self.listen_for_result(window))
            return

        self.meta_info.finished = False
        self.new_thread = threading.Thread(
            # target=runloop,
            target=run,
            kwargs={'meta_info':self.meta_info})
        self.new_thread.start()
        window.after(50, lambda: self.listen_for_result(window))

    def listen_for_result(self, window):
        # TODO setting the maximum here is not optimal but its better than doing it in the modifier
        c_count = self.meta_info.chunk_count
        c_count_max = self.meta_info.chunk_count_max
        f_count = self.meta_info.file_count
        f_count_max = self.meta_info.file_count_max
        self.chunk_progress["value"] = c_count
        self.chunk_progress["maximum"] = c_count_max
        self.chunk_progress.update()

        self.file_progress["value"] = f_count
        self.file_progress["maximum"] = f_count_max
        self.file_progress.update()

        if not self.meta_info.text_queue.empty():
            self.details_text.insert(END, self.meta_info.text_queue.get(0))

        if self.meta_info.finished:
            self.chunk_label.config(text=f"Finished all chunks of {c_count_max} chunks.")
            self.file_label.config(text=f"Finished all files of {f_count_max} files.")
            self.time_label.config(text=f"Done.")

            # TODO check this
            while not self.meta_info.text_queue.empty():
                self.details_text.insert(END, self.meta_info.text_queue.get(0))
        else:
            max_chunk = int(math.sqrt(c_count_max))
            c_x = int(c_count % 32)
            c_z = int(c_count / 32)

            s = int(self.meta_info.estimated_time % 60)
            m = int(self.meta_info.estimated_time / 60)
            self.time_label.config(text=f"Processing Data. Estimated rest time: {m} minutes and {s} seconds.")

            # TODO hmmm
            if c_count == c_count_max:
                c_x = max_chunk - 1
                c_z = max_chunk - 1
                self.time_label.config(text=f"Writing File. Estimated rest time: 5 minutes.")

            self.chunk_label.config(
                text=f"Finished chunk ({c_x}, {c_z}) of ({max_chunk - 1}, {max_chunk - 1}). And {c_count} of {c_count_max} chunks.")
            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            window.after(50, lambda: self.listen_for_result(window))

    # 17
    # 12
    #

    ###############################################################################################
    # Initialisation functions
    ###############################################################################################
    def init_resource_folder(self, window):

        def browse_button(dir, initial):
            filename = filedialog.askdirectory(initialdir = initial)
            dir.set(filename)

        self.meta_info.set_dirs(S_DIR, S_DIR + "_replacement", S_DIR + "_copy")

        # TODO the other directorys are not updated automatically if the first one changes
        # but obacht that should not happen if the 2nd or 3rd are already changed
        source_button = Button(window, text="Browse for source directory.", command=lambda: browse_button(self.meta_info.source_dir, S_DIR))
        source_button.grid(row=0, column=0, pady = PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.source_dir)
        lbl1.grid(row=1, column=0, padx = PAD_X, pady = PAD_Y)

        replacement_button = Button(window, text="Browse for replacement directory.", command=lambda: browse_button(self.meta_info.replacement_dir, S_DIR + "_replacement"))
        replacement_button.grid(row=2, column=0, pady = PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.replacement_dir)
        lbl1.grid(row=3, column=0, padx = PAD_X, pady = PAD_Y)

        target_button = Button(window, text="Browse for target directory.", command=lambda: browse_button(self.meta_info.target_dir, S_DIR + "_copy"))
        target_button.grid(row=4, column=0, pady = PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.target_dir)
        lbl1.grid(row=5, column=0, padx = PAD_X, pady = 10)

    def init_checkbuttons(self, window):
        # Create checkboxes
        Checkbutton(window, text="Fix pockets in water.", variable=self.meta_info.water_blocks).grid(row=6, sticky=W, padx = PAD_X)
        Checkbutton(window, text="Fix air pockets.", variable=self.meta_info.air_pockets).grid(row=7, sticky=W, padx = PAD_X)
        Checkbutton(window, text="Use replacement blocks from other map.", variable=self.meta_info.repl_blocks).grid(row=8, sticky=W, padx = PAD_X)

        # TODO give option to select block amount
        # Label(master, text="First Name").grid(row=0)
        # Label(master, text="Last Name").grid(row=1)
        Entry(window, width=5).grid(row=6, sticky=E, padx = (0, 20))
        Entry(window, width=5).grid(row=7, sticky=E, padx = (0, 20))
        Entry(window, width=5).grid(row=8, sticky=E, padx = (0, 20))

    def init_progressindicator(self, window):
        # Update to get the correct width for the progressbar
        window.update()
        # Progress bar widget
        self.chunk_progress = Progressbar(window, orient = HORIZONTAL, length = window.winfo_width(), mode = 'determinate')
        self.chunk_progress["value"] = 0
        self.chunk_progress.update()
        self.chunk_progress.grid(row=9, sticky=W, padx = PAD_X, pady = 10)

        self.file_progress = Progressbar(window, orient = HORIZONTAL, length = window.winfo_width(), mode = 'determinate')
        self.file_progress["value"] = 0
        self.file_progress.update()
        self.file_progress.grid(row=11, sticky=W, padx = PAD_X, pady = 10)

        # Progress label
        self.chunk_label = Label(window, text="Program is not yet running!")
        self.chunk_label.grid(row=10, sticky=E, padx = PAD_X)
        self.file_label = Label(window, text="Program is not yet running!")
        self.file_label.grid(row=12, sticky=E, padx = PAD_X)

        self.time_label = Label(window, text="")
        self.time_label.grid(row=13, sticky=E, padx = PAD_X)

    def init_details(self, window):
        # Create details button
        def details():
            if helper_frame.hidden:
                helper_frame.grid()
                helper_frame.hidden = False
                self.run_button.grid(row=15)
            else:
                helper_frame.grid_remove()
                helper_frame.hidden = True
                self.run_button.grid(row=14)

        details_button = Button(window, text="Details", command=details)
        details_button.grid(row=13, column=0, sticky=W, padx = PAD_X)

        # Details Menu
        helper_frame = Frame(window, width=window.winfo_width() - PAD_X * 2, height=100)
        helper_frame.pack_propagate(False)
        self.details_text = Text(helper_frame, width=0, height=0)
        details_scroll = Scrollbar(helper_frame, command=self.details_text.yview)
        details_scroll.pack(side=RIGHT, fill=Y)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        self.details_text.pack(fill="both", expand=True)
        helper_frame.grid(row=14, column=0, padx = PAD_X, pady = 10)
        helper_frame.grid_remove()
        helper_frame.hidden = True

###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    window.title("mc-map-modifier")
    main_app = MainApp(window)
    window.mainloop()
