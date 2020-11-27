from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *

# Needed for the username
import os

# own imports
from modifier import run

# Create the window
window = Tk()
# Set the title
window.title("mc-map-modifier")

PAD_X = 20

# Test path
S_DIR = "C:/Users/"+os.getlogin()+"/Projekte/mc-map-modifier/original"
R_DIR = "C:/Users/"+os.getlogin()+"/Projekte/mc-map-modifier/original_replacement"

#S_DIR = "C:/Users/"+os.getlogin()+"/AppData/Roaming/.minecraft/saves"
#R_DIR = "C:/Users/"+os.getlogin()+"/AppData/Roaming/.minecraft/saves"

def browse_button(dir, initial):
    filename = filedialog.askdirectory(initialdir = initial)
    dir.set(filename)

source_dir = StringVar()
source_dir.set(S_DIR)
source_button = Button(window, text="Browse for source directory.", command=lambda: browse_button(source_dir, S_DIR))
source_button.grid(row=0, column=0, pady = (10, 0))
lbl1 = Label(window, textvariable=source_dir)
lbl1.grid(row=1, column=0, padx = PAD_X, pady = (10, 0))

replacement_dir = StringVar()
replacement_dir.set(R_DIR)
replacement_button = Button(window, text="Browse for replacement directory.", command=lambda: browse_button(replacement_dir, R_DIR))
replacement_button.grid(row=2, column=0, pady = (10, 0))
lbl1 = Label(window, textvariable=replacement_dir)
lbl1.grid(row=3, column=0, padx = PAD_X, pady = 10)

# T_DIR = source_dir + "_copy"
# target_dir = StringVar()
# target_dir.set(T_DIR)
# target_button = Button(window, text="Browse for target directory.", command=lambda: browse_button(target_dir, T_DIR))
# target_button.grid(row=4, column=0, pady = (10, 0))
# lbl1 = Label(window, textvariable=target_dir)
# lbl1.grid(row=5, column=0, padx = PAD_X, pady = 10)

# TODO add target folder

# Create checkboxes
# TODO give option to select block amount
water_blocks = IntVar()
Checkbutton(window, text="Fix pockets in water.", variable=water_blocks).grid(row=4, sticky=W, padx = PAD_X)
air_blocks = IntVar()
Checkbutton(window, text="Fix air pockets.", variable=air_blocks).grid(row=5, sticky=W, padx = PAD_X)
new_blocks = IntVar()
Checkbutton(window, text="Use replacement blocks from other map.", variable=new_blocks).grid(row=6, sticky=W, padx = PAD_X)

# Update to get the correct width for the progressbar
window.update()
# Progress bar widget
chunk_progress = Progressbar(window, orient = HORIZONTAL, length = window.winfo_width(), mode = 'determinate')
chunk_progress["value"] = 0
chunk_progress.update()
chunk_progress.grid(row=7, sticky=W, padx = PAD_X, pady = 10)

file_progress = Progressbar(window, orient = HORIZONTAL, length = window.winfo_width(), mode = 'determinate')
file_progress["value"] = 0
file_progress.update()
file_progress.grid(row=9, sticky=W, padx = PAD_X, pady = 10)

# Progress label
chunk_label = Label(window, text="")
chunk_label.grid(row=8, sticky=W, padx = PAD_X)
files_label = Label(window, text="")
files_label.grid(row=10, sticky=W, padx = PAD_X)

# Create details button
def details():
    if helper_frame.hidden:
        helper_frame.grid()
        helper_frame.hidden = False
        run_button.grid(row=12)
    else:
        helper_frame.grid_remove()
        helper_frame.hidden = True
        run_button.grid(row=11)

details_button = Button(window, text="Details", command=details)
details_button.grid(row=10, column=0, sticky=E, padx = PAD_X)

# Details Menu
helper_frame = Frame(window, width=window.winfo_width() - PAD_X * 2, height=100)
helper_frame.pack_propagate(False)
details_text = Text(helper_frame, width=0, height=0)
details_scroll = Scrollbar(helper_frame, command=details_text.yview)
details_scroll.pack(side=RIGHT, fill=Y)
details_text.configure(yscrollcommand=details_scroll.set)
details_text.pack(fill="both", expand=True)
helper_frame.grid(row=11, column=0, padx = PAD_X, pady = 10)
helper_frame.grid_remove()
helper_frame.hidden = True

# Create run button
run_button = Button(window, text="Dew it", command=lambda: run(
    source_dir.get(),
    chunk_progress, file_progress, chunk_label, files_label,
    water_blocks.get(), air_blocks.get(), new_blocks.get(),
    details_text)
)
run_button.grid(row=11, column=0, padx = PAD_X, pady = 10)

window.mainloop()
