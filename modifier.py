# minecraft import
import anvil

# Needed for the file iteration
import os

# For array manipulations
import numpy as np

# Utilities
from math import floor

# TODO
# Timing
import time
import datetime
from time import gmtime, strftime

# TODO
# Gui
from tkinter import messagebox

# Own imports
from identifier import Identifier
from classifier_mp import ClassifierMP
from block_tests import is_solid

import config as cfg

class Modifier():
    def __init__(self, meta_info):
        self.meta_info = meta_info

        # TODO
        self.changeCountWater = 0
        self.changeCountAir = 0
        self.changeCountRepl = 0

    ###############################################################################################
    # Copy
    ###############################################################################################
    def modify(self, chunk, replChunk, newRegion, chunk_x, chunk_z):
        newChunk = 0
        x = 0
        y = 0
        z = 0

        # Create `Block` objects that are used to set blocks
        stone = anvil.Block('minecraft', 'stone')
        water = anvil.Block('minecraft', 'water')
        diamond_block = anvil.Block('minecraft', 'diamond_block')
        gold_block = anvil.Block('minecraft', 'gold_block')
        blue_wool = anvil.Block('minecraft', 'blue_wool')

        # Iterate all blocks and select write the new block to the newChunk
        for block in chunk.stream_chunk():
            b = block

            x_region = chunk_x * 16 + x
            z_region = chunk_z * 16 + z
            x_global = newRegion.x * 512 + x_region
            z_global = newRegion.z * 512 + z_region

            xyz = self.identifier.identified[x_region, y, z_region]
            if xyz == cfg.WATERBLOCK:
                b = water
                print(f'Found water Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            elif xyz == cfg.AIRPOCKET:
                b = gold_block
                # if replChunk:
                #     newBlock = replChunk.get_block(x, y, z)
                #     # TODO expand is_solid list
                #     if is_solid(newBlock.id):
                #         b = newBlock
                #         b = blue_wool
                print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            elif xyz == cfg.SOLIDAREA:
            # if xyz == SOLIDAREA:
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    # Replace the block if it is solid but use the original when it is not
                    if is_solid(newBlock.id):
                        b = newBlock
                    # TODO debug version
                    b = diamond_block
            # elif xyz == UNCHECKED:
            #     print(f'Found unchecked Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z}), this should not happen')
                #print(f'GlobalPos: ({newRegion.x * 512 + chunk_x * 16 + x}, {y}, {newRegion.z * 512 + chunk_z * 16 + z})')
            elif xyz != cfg.UNCHANGED2:
                print(f'Found unidentified Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunchunk_zkZ}) with {xyz}, this should not happen')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')

            try:
                newChunk = newRegion.set_block(b, x_global, y, z_global)
            except:
                print(f'could not set Block ({x},{y},{z})')

            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        newChunk.set_data(chunk.data)

    ###############################################################################################

    def copy_chunk(self, new_region, region, repl_region, chunk_x, chunk_z):
        chunk = None
        try:
            chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
        except:
            print(f'skipped non-existent chunk ({chunk_x},{chunk_z})')

        if chunk:
            # TODO only when the option is ticked?
            repl_chunk = False
            if repl_region:
                try:
                    repl_chunk = anvil.Chunk.from_region(repl_region, chunk_x, chunk_z)
                except:
                    print(f'Could not create replacement chunk for {chunk_x}, {chunk_z}.')

            self.modify(chunk, repl_chunk, new_region, chunk_x, chunk_z)

    ###############################################################################################

    def copy_chunks(self, newRegion, region, replRegion):
        ms = int(round(time.time() * 1000))

        classifier_mp = ClassifierMP()
        classifier_mp.classify_all_mp(region)
        # TODO does the modifier need this?
        self.classified_air_region = classifier_mp.classified_air_region
        self.classified_water_region = classifier_mp.classified_water_region
        self.classified_repl_region = classifier_mp.classified_repl_region

        ms2 = int(round(time.time() * 1000))
        print(f"Classifier time: {ms2 - ms}")

        self.identifier = Identifier(self.meta_info, True)
        # TODO names and delete the counts here
        self.changeCountWater, self.changeCountAir, self.changeCountRepl = self.identifier.identify(self.classified_air_region, self.classified_water_region, self.classified_repl_region)

        ms3 = int(round(time.time() * 1000))
        print(f"Identifier time: {ms3 - ms2}")

        for chunk_x in range(cfg.REGION_C_X):
        # for chunk_x in range(10, 12):

            ms = int(round(time.time() * 1000))
            for chunk_z in range(cfg.REGION_C_Z):
            # for chunk_z in range(11, 16):
                self.copy_chunk(newRegion, region, replRegion, chunk_x, chunk_z)
                self.meta_info.chunk_count = chunk_z + 1 + chunk_x * cfg.REGION_C_Z

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk

        ms4 = int(round(time.time() * 1000))
        print(f"Modify time: {ms4 - ms3}")

    ###############################################################################################

    def copyRegion(self, filename):
        l = filename.split('.')
        rX = int(l[1])
        rZ = int(l[2])

        ms = int(round(time.time() * 1000))

        # Create a new region with the `EmptyRegion` class at region coords
        newRegion = anvil.EmptyRegion(rX, rZ)
        src_dir = self.meta_info.source_dir.get()
        region = anvil.Region.from_file(src_dir + "/" + filename)

        replRegion = False
        if self.repl_blocks:
            try:
                repl_dir = self.meta_info.replacement_dir.get()
                replRegion = anvil.Region.from_file(repl_dir + "/" + filename)
            except:
                print(f'Could not create replacement region for {filename}.')

        ms2 = int(round(time.time() * 1000))
        print(f"Setup regions time: {ms2 - ms}")

        # TODO use config file
        self.meta_info.chunk_count = 0
        self.meta_info.chunk_count_max = cfg.REGION_C_X * cfg.REGION_C_Z
        # TODO calculation not correct anymore
        self.meta_info.estimated_time = self.meta_info.chunk_count_max * self.meta_info.file_count_max

##########################################

        self.copy_chunks(newRegion, region, replRegion)

##########################################

        # TODO changeCountAir is not reset
        if self.water_blocks + self.air_pockets + self.repl_blocks >= 1:
            self.meta_info.text_queue.put(f'In file {filename}:\n')
        if self.water_blocks == 1:
            self.meta_info.text_queue.put(f'Changed {self.changeCountWater} solid blocks to water.\n')
        if self.air_pockets == 1:
            self.meta_info.text_queue.put(f'Changed {self.changeCountAir} air blocks to solid blocks.\n')
        if self.repl_blocks == 1:
            self.meta_info.text_queue.put(f'Changed {self.changeCountRepl} solid blocks to replacement solid blocks.\n')

        ms = int(round(time.time() * 1000))

        # Save to a file
        target_dir = self.meta_info.target_dir.get()
        newRegion.save(target_dir + "/" + filename)

        ms2 = int(round(time.time() * 1000))
        print(f"Save time: {ms2 - ms}")

###################################################################################################
# Main
###################################################################################################
    def run2(self):
        # https://www.machinelearningplus.com/python/cprofile-how-to-profile-your-python-code/
        import cProfile, pstats
        profiler = cProfile.Profile()
        profiler.enable()
        self.run2()
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        stats.print_stats()
        #import cProfile
        #cProfile.run('self.run2()')

    def run(self):
        self.water_blocks = self.meta_info.water_blocks.get()
        self.air_pockets = self.meta_info.air_pockets.get()
        self.repl_blocks = self.meta_info.repl_blocks.get()

        # Print detailed informations
        if (self.water_blocks == 1):
            self.meta_info.text_queue.put("Water Blocks will be fixed!\n")
        else:
            self.meta_info.text_queue.put("Water Blocks will not be fixed!\n")

        if (self.air_pockets  == 1):
            self.meta_info.text_queue.put("Air Blocks will be fixed!\n")
        else:
            self.meta_info.text_queue.put("Air Blocks will not be fixed!\n")

        if (self.repl_blocks == 1):
            self.meta_info.text_queue.put("Replacement Blocks will be inserted!\n")
        else:
            self.meta_info.text_queue.put("Replacement Blocks will not be inserted!\n")

        self.meta_info.text_queue.put("\n.. starting\n")
        t1 = gmtime()
        self.meta_info.text_queue.put(strftime("%Y-%m-%d %H:%M:%S\n", t1))
        ms = int(round(time.time() * 1000))

        # Get all files in the directory
        filelist = os.listdir(self.meta_info.source_dir.get())
        if len(filelist) == 0:
            messagebox.showinfo(message="No files found! Select a different source path.", title = "Error")
            return

        tgt_dir = self.meta_info.target_dir.get()
        try:
            if not os.path.exists(tgt_dir):
                os.mkdir(tgt_dir)
        except OSError:
            messagebox.showinfo(message="Creation of the directory %s failed" % tgt_dir, title = "Error")

        # Update the progressbar and label for the files
        self.meta_info.file_count_max = len(filelist)

        # Iterate the files
        i = 1
        for filename in filelist:
            if filename.endswith(".mca"):
                # TODO combine path and filename here ?
                self.copyRegion(filename)
            else:
                continue
            self.meta_info.file_count = i
            i += 1

        # Print that the process is finished
        self.meta_info.text_queue.put("\n.. finished\n")
        t2 = gmtime()
        self.meta_info.text_queue.put(strftime("%Y-%m-%d %H:%M:%S\n", t2))
        self.meta_info.text_queue.put("Total runtime: ")
        self.meta_info.text_queue.put(datetime.timedelta(seconds=time.mktime(t2)-time.mktime(t1)))

        ms2 = int(round(time.time() * 1000))
        print(f"Total time elapsed: {ms2 - ms}")

        self.meta_info.finished = True
