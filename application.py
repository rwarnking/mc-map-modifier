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

def browse_button(dir):
    filename = filedialog.askdirectory(initialdir = "C:/Users/"+os.getlogin()+"/AppData/Roaming/.minecraft/saves")
    dir.set(filename)

source_dir = StringVar()
source_button = Button(window, text="Browse for source directory.", command=lambda: browse_button(source_dir))
source_button.grid(row=0, column=0)
lbl1 = Label(window, textvariable=source_dir)
lbl1.grid(row=1, column=0)

replacment_dir = StringVar()
replacment_button = Button(window, text="Browse for replacment directory.", command=lambda: browse_button(replacment_dir))
replacment_button.grid(row=2, column=0)
lbl1 = Label(window, textvariable=replacment_dir)
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
progress = Progressbar(window, orient = HORIZONTAL, length = 300, mode = 'determinate')
progress["value"] = 0
progress.update()
progress.grid(row=7, sticky=W, padx = 20, pady = 10)

# Progress label
chunk_label = Label(window, text="")
chunk_label.grid(row=8, sticky=W, padx = 20)
files_label = Label(window, text="")
files_label.grid(row=9, sticky=W, padx = 20)

# Create Buttons
run_button = Button(window, text="Dew it", command=lambda: run(progress, chunk_label, files_label, water_blocks, air_blocks, new_blocks))
run_button.grid(row=10, column=0, padx = 20, pady = 10)

window.mainloop()
