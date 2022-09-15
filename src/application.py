import os  # Needed for the username
import threading
from tkinter import (
    END,
    HORIZONTAL,
    RIGHT,
    Button,
    Entry,
    Frame,
    Label,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Progressbar, Scrollbar

# own imports
import config as cfg
from meta_information import MetaInformation
from task_manager import TaskManager

PAD_X = 20
PAD_Y = (10, 0)

# Test path
# TODO config?
S_DIR = "C:/Users/" + os.getlogin() + "/Projekte/mc-map-modifier/original"
# S_DIR = "C:/Users/" + os.getlogin() + "/AppData/Roaming/.minecraft/saves"
# R_DIR = "C:/Users/" + os.getlogin() + "/AppData/Roaming/.minecraft/saves"


class MainApp:
    def __init__(self, window):
        self.meta_info = MetaInformation()

        self.row_idx = 0

        self.init_resource_folder(window)
        self.init_checkbuttons(window)
        self.init_tunnel_input(window)
        self.init_progressindicator(window)
        self.init_details(window)

        self.run_button = Button(window, text="Dew it", command=lambda: self.run(window))
        self.run_button.grid(row=self.row_idx, column=0, padx=PAD_X, pady=10)

    def on_closing(self):
        # In case the program is running, check if it really should be closed
        if not self.meta_info.finished:
            if messagebox.askokcancel("Quit", "Program is running, do you really want to quit?"):
                window.destroy()
        else:
            window.destroy()

    def row(self):
        self.row_idx += 1
        return self.row_idx - 1

    def run(self, window):
        if not self.meta_info.finished:
            messagebox.showinfo(message="Modification is already happening.", title="Error")
            window.after(50, lambda: self.listen_for_result(window))
            return

        tm = TaskManager(self.meta_info)
        self.meta_info.finished = False
        self.new_thread = threading.Thread(target=tm.run, daemon=True)
        self.new_thread.start()
        window.after(50, lambda: self.listen_for_result(window))

    def listen_for_result(self, window):
        # TODO setting the maximum here is not optimal but its better than doing it in the modifier
        c_count = self.meta_info.get_current_count()
        c_count_max = self.meta_info.get_current_max_count()
        f_count = self.meta_info.counts.file_count
        f_count_max = self.meta_info.counts.file_count_max
        self.chunk_progress["value"] = c_count
        self.chunk_progress["maximum"] = c_count_max
        self.chunk_progress.update()

        self.algo_progress["value"] = self.meta_info.counts.algo_step
        self.algo_progress["maximum"] = self.meta_info.counts.algo_step_max
        self.algo_progress.update()

        self.file_progress["value"] = f_count
        self.file_progress["maximum"] = f_count_max
        self.file_progress.update()

        if not self.meta_info.text_queue.empty():
            self.details_text.insert(END, self.meta_info.text_queue.get(0))

        if self.meta_info.finished:
            self.chunk_label.config(text=f"Finished all chunks of {c_count_max} chunks.")
            self.algo_label.config(
                text=f"Finished all {self.meta_info.counts.algo_step_max} steps."
            )
            self.file_label.config(text=f"Finished all files of {f_count_max} files.")
            self.time_label.config(text="Done.")

            # TODO check this
            while not self.meta_info.text_queue.empty():
                self.details_text.insert(END, self.meta_info.text_queue.get(0))
        else:
            c_x = int(c_count % cfg.REGION_C_Z)
            c_z = int(c_count / cfg.REGION_C_Z)

            self.meta_info.update_estimated_time()
            s = int(self.meta_info.timer.estimated_time % 60)
            m = int(self.meta_info.timer.estimated_time / 60)
            self.time_label.config(
                text=f"Processing Data. Estimated rest time: {m} minutes and {s} seconds."
            )

            if self.meta_info.counts.algo_step == cfg.A_SAVE:
                c_x = cfg.REGION_C_X - 1
                c_z = cfg.REGION_C_Z - 1
                self.time_label.config(text="Writing File. Estimated rest time: 3 minutes.")

            if (
                self.meta_info.counts.algo_step != cfg.A_IDENTIFY and
                self.meta_info.counts.algo_step != cfg.A_MODIFY
            ):
                self.chunk_label.config(
                    text=(
                        f"Finished chunk ({c_x}, {c_z}) of "
                        f"({cfg.REGION_C_X - 1}, {cfg.REGION_C_Z - 1}). "
                        f"And {c_count} of {c_count_max} chunks."
                    )
                )
            else:
                self.chunk_label.config(text=f"Finished {c_count} of {c_count_max} elements.")
            self.algo_label.config(
                text=(
                    f"Finished {self.meta_info.counts.algo_step} "
                    f"out of {self.meta_info.counts.algo_step_max} steps."
                )
            )
            self.file_label.config(text=f"Finished file {f_count} of {f_count_max} files.")
            window.after(50, lambda: self.listen_for_result(window))

    ###############################################################################################
    # Initialisation functions
    ###############################################################################################
    def init_resource_folder(self, window):
        def browse_button(dir, initial):
            filename = filedialog.askdirectory(initialdir=initial)
            if filename:
                dir.set(filename)

        self.meta_info.set_dirs(S_DIR, S_DIR + "_replacement", S_DIR + "_copy")

        # TODO the other directorys are not updated automatically if the first one changes
        # but obacht that should not happen if the 2nd or 3rd are already changed
        source_button = Button(
            window,
            text="Browse for source directory.",
            command=lambda: browse_button(self.meta_info.source_dir, S_DIR),
        )
        source_button.grid(row=self.row(), column=0, pady=PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.source_dir)
        lbl1.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y)

        replacement_button = Button(
            window,
            text="Browse for replacement directory.",
            command=lambda: browse_button(self.meta_info.replacement_dir, S_DIR + "_replacement"),
        )
        replacement_button.grid(row=self.row(), column=0, pady=PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.replacement_dir)
        lbl1.grid(row=self.row(), column=0, padx=PAD_X, pady=PAD_Y)

        target_button = Button(
            window,
            text="Browse for target directory.",
            command=lambda: browse_button(self.meta_info.target_dir, S_DIR + "_copy"),
        )
        target_button.grid(row=self.row(), column=0, pady=PAD_Y)
        lbl1 = Label(window, textvariable=self.meta_info.target_dir)
        lbl1.grid(row=self.row(), column=0, padx=PAD_X, pady=10)

    def init_checkbuttons(self, window):
        vcmd = window.register(lambda P: str.isdigit(P))
        e_pad_x = (0, 20)
        l_pad_x = (0, 20 + 2 * 10)

        Checkbutton(window, text="Fix air pockets.", variable=self.meta_info.air_pockets).grid(
            row=self.row_idx, sticky="W", padx=PAD_X
        )
        Label(window, text="Num blocks: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x)
        Entry(
            window,
            textvariable=self.meta_info.apocket_size,
            width=2,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row(), sticky="E", padx=e_pad_x)

        Checkbutton(
            window, text="Fix pockets in water.", variable=self.meta_info.water_blocks
        ).grid(row=self.row_idx, sticky="W", padx=PAD_X)
        Label(window, text="Num blocks: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x)
        Entry(
            window,
            textvariable=self.meta_info.wpocket_size,
            width=2,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row(), sticky="E", padx=e_pad_x)

        Checkbutton(
            window, text="Use replacement blocks.", variable=self.meta_info.repl_blocks
        ).grid(row=self.row_idx, sticky="W", padx=PAD_X)
        Label(window, text="Neighbourhood: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x)
        Entry(
            window,
            textvariable=self.meta_info.repl_area,
            width=2,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row(), sticky="E", padx=e_pad_x)

    def init_tunnel_input(self, window):
        vcmd = window.register(lambda P: str.isdigit(P))
        width = 4
        char_size = 7.5
        text = 20
        e_pad_x1 = (0, PAD_X)
        e_pad_x2 = (0, e_pad_x1[1] + width * char_size + text)
        e_pad_x3 = (0, e_pad_x2[1] + width * char_size + text)
        l_pad_x1 = (0, e_pad_x1[1] + width * char_size)
        l_pad_x2 = (0, e_pad_x2[1] + width * char_size)
        l_pad_x3 = (0, e_pad_x3[1] + width * char_size)

        Checkbutton(
            window, text="Add Tunnel (global coordinates):", variable=self.meta_info.add_tunnel
        ).grid(
            row=self.row(), sticky="W", padx=PAD_X
        )

        Label(window, text="Start ").grid(row=self.row_idx, sticky="W", padx=PAD_X)
        Label(window, text="x: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x3)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_start_x,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row_idx, sticky="E", padx=e_pad_x3)
        Label(window, text="y: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x2)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_start_y,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row_idx, sticky="E", padx=e_pad_x2)
        Label(window, text="z: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x1)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_start_z,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row(), sticky="E", padx=e_pad_x1)

        Label(window, text="End ").grid(row=self.row_idx, sticky="W", padx=PAD_X)
        Label(window, text="x: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x3)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_end_x,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row_idx, sticky="E", padx=e_pad_x3)
        Label(window, text="y: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x2)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_end_y,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row_idx, sticky="E", padx=e_pad_x2)
        Label(window, text="z: ").grid(row=self.row_idx, sticky="E", padx=l_pad_x1)
        Entry(
            window,
            textvariable=self.meta_info.tunnel_end_z,
            width=4,
            validate="all",
            validatecommand=(vcmd, "%P"),
        ).grid(row=self.row(), sticky="E", padx=e_pad_x1)

    def init_progressindicator(self, window):
        # Update to get the correct width for the progressbar
        window.update()
        w_width = window.winfo_width()
        # Progress bar 1
        self.chunk_progress = Progressbar(
            window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.chunk_progress["value"] = 0
        self.chunk_progress.update()
        self.chunk_progress.grid(row=self.row(), sticky="W", padx=PAD_X, pady=10)
        # Progress label
        self.chunk_label = Label(window, text="Program is not yet running!")
        self.chunk_label.grid(row=self.row(), sticky="E", padx=PAD_X)

        # Progress bar 2
        self.algo_progress = Progressbar(
            window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.algo_progress["value"] = 0
        self.algo_progress.update()
        self.algo_progress.grid(row=self.row(), sticky="W", padx=PAD_X, pady=10)
        # Progress label
        self.algo_label = Label(window, text="Program is not yet running!")
        self.algo_label.grid(row=self.row(), sticky="E", padx=PAD_X)

        # Progress bar 3
        self.file_progress = Progressbar(
            window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.file_progress["value"] = 0
        self.file_progress.update()
        self.file_progress.grid(row=self.row(), sticky="W", padx=PAD_X, pady=10)
        # Progress label
        self.file_label = Label(window, text="Program is not yet running!")
        self.file_label.grid(row=self.row(), sticky="E", padx=PAD_X)

        self.time_label = Label(window, text="")
        self.time_label.grid(row=self.row_idx, sticky="E", padx=PAD_X)

    def init_details(self, window):
        # Create details button
        def details():
            if helper_frame.hidden:
                helper_frame.grid()
                helper_frame.hidden = False
                self.run_button.grid(row=self.row_idx + 1)
            else:
                helper_frame.grid_remove()
                helper_frame.hidden = True
                self.run_button.grid(row=self.row_idx)

        details_button = Button(window, text="Details", command=details)
        details_button.grid(row=self.row(), column=0, sticky="W", padx=PAD_X)

        # Details Menu
        helper_frame = Frame(window, width=window.winfo_width() - PAD_X * 2, height=100)
        helper_frame.pack_propagate(False)
        self.details_text = Text(helper_frame, width=0, height=0)
        details_scroll = Scrollbar(helper_frame, command=self.details_text.yview)
        details_scroll.pack(side=RIGHT, fill="y")
        self.details_text.configure(yscrollcommand=details_scroll.set)
        self.details_text.pack(fill="both", expand=True)
        helper_frame.grid(row=self.row_idx, column=0, padx=PAD_X, pady=10)
        helper_frame.grid_remove()
        helper_frame.hidden = True


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    window.title("mc-map-modifier")
    main_app = MainApp(window)
    window.protocol("WM_DELETE_WINDOW", main_app.on_closing)
    window.mainloop()
