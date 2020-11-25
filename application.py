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
source_button.grid(row=0, column=0, pady = 10)
lbl1 = Label(window, textvariable=source_dir)
lbl1.grid(row=1, column=0)

replacement_dir = StringVar()
replacement_dir.set(R_DIR)
replacement_button = Button(window, text="Browse for replacement directory.", command=lambda: browse_button(replacement_dir, R_DIR))
replacement_button.grid(row=2, column=0, pady = 10)
lbl1 = Label(window, textvariable=replacement_dir)
lbl1.grid(row=3, column=0)

# TODO add target folder

# Create checkboxes
water_blocks = IntVar()
Checkbutton(window, text="water_blocks", variable=water_blocks).grid(row=4, sticky=W, padx = 20)
air_blocks = IntVar()
Checkbutton(window, text="air_blocks", variable=air_blocks).grid(row=5, sticky=W, padx = 20)
new_blocks = IntVar()
Checkbutton(window, text="new_blocks", variable=new_blocks).grid(row=6, sticky=W, padx = 20)

# Progress bar widget
chunk_progress = Progressbar(window, orient = HORIZONTAL, length = 300, mode = 'determinate')
chunk_progress["value"] = 0
chunk_progress.update()
chunk_progress.grid(row=7, sticky=W, padx = 20, pady = 10)

file_progress = Progressbar(window, orient = HORIZONTAL, length = 300, mode = 'determinate')
file_progress["value"] = 0
file_progress.update()
file_progress.grid(row=9, sticky=W, padx = 20, pady = 10)

# Progress label
chunk_label = Label(window, text="")
chunk_label.grid(row=8, sticky=W, padx = 20)
files_label = Label(window, text="")
files_label.grid(row=10, sticky=W, padx = 20)

# Create Buttons
run_button = Button(window, text="Dew it", command=lambda: run(source_dir.get(), chunk_progress, file_progress, chunk_label, files_label, water_blocks, air_blocks, new_blocks))
run_button.grid(row=11, column=0, padx = 20, pady = 10)

window.mainloop()
