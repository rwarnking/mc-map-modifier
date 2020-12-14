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

        self.identifier = Identifier(self.meta_info)

    ###############################################################################################
    # Main
    ###############################################################################################
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
        self.air_pockets = self.meta_info.air_pockets.get()
        self.water_blocks = self.meta_info.water_blocks.get()
        self.repl_blocks = self.meta_info.repl_blocks.get()

        # Print detailed informations
        # TODO improve
        if (self.air_pockets == 1):
            self.meta_info.text_queue.put("Air Blocks will be fixed!\n")
        else:
            self.meta_info.text_queue.put("Air Blocks will not be fixed!\n")

        if (self.water_blocks == 1):
            self.meta_info.text_queue.put("Water Blocks will be fixed!\n")
        else:
            self.meta_info.text_queue.put("Water Blocks will not be fixed!\n")

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

    ###############################################################################################

    def copyRegion(self, filename):
        l = filename.split('.')
        rX = int(l[1])
        rZ = int(l[2])

        # Create a new region with the `EmptyRegion` class at region coords
        new_region = anvil.EmptyRegion(rX, rZ)
        src_dir = self.meta_info.source_dir.get()
        region = anvil.Region.from_file(src_dir + "/" + filename)

        repl_region = False
        if self.repl_blocks:
            try:
                repl_dir = self.meta_info.replacement_dir.get()
                repl_region = anvil.Region.from_file(repl_dir + "/" + filename)
            except:
                print(f'Could not create replacement region for {filename}.')

        ##########################################
        # Main function call
        ##########################################
        self.copy_chunks(new_region, region, repl_region)

        if self.water_blocks + self.air_pockets + self.repl_blocks >= 1:
            self.meta_info.text_queue.put(f'In file {filename}:\n')
        if self.air_pockets == 1:
            self.meta_info.text_queue.put(f'Changed {self.meta_info.counts.changed_air.value} air blocks to solid blocks.\n')
        if self.water_blocks == 1:
            self.meta_info.text_queue.put(f'Changed {self.meta_info.counts.changed_water.value} solid blocks to water.\n')
        if self.repl_blocks == 1:
            self.meta_info.text_queue.put(f'Changed {self.meta_info.counts.changed_repl.value} solid blocks to replacement solid blocks.\n')

        ms = int(round(time.time() * 1000))

        # Save to a file
        self.meta_info.algo_step = cfg.A_SAVE
        target_dir = self.meta_info.target_dir.get()
        new_region.save(target_dir + "/" + filename)
        self.meta_info.algo_step = cfg.A_FINISHED

        ms2 = int(round(time.time() * 1000))
        print(f"Save time: {ms2 - ms}")

    ###############################################################################################

    def copy_chunks(self, new_region, region, repl_region):
        ms = int(round(time.time() * 1000))

        # TODO combine these into a function?
        self.meta_info.algo_step = cfg.A_CLASSIFY
        self.meta_info.counts.chunks.value = 0
        classifier_mp = ClassifierMP(self.meta_info)
        if self.air_pockets + self.repl_blocks + self.water_blocks > 0:
            classifier_mp.classify_all_mp(region, self.meta_info.counts.chunks)

        ms2 = int(round(time.time() * 1000))
        print(f"Classifier time: {ms2 - ms}")

        self.meta_info.algo_step = cfg.A_IDENTIFY
        self.identifier.identify(classifier_mp.c_regions, self.meta_info.counts)

        ms3 = int(round(time.time() * 1000))
        print(f"Identifier time: {ms3 - ms2}")

        self.meta_info.algo_step = cfg.A_MODIFY
        self.meta_info.counts.chunks.value = 0
        for chunk_x in range(cfg.REGION_C_X):

            self.meta_info.start_time()
            for chunk_z in range(cfg.REGION_C_Z):
                self.copy_chunk(new_region, region, repl_region, chunk_x, chunk_z)
                self.meta_info.counts.chunks.value += 1

            self.meta_info.end_time()
            self.meta_info.update_elapsed()

        ms4 = int(round(time.time() * 1000))
        print(f"Modify time: {ms4 - ms3}")

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

    def modify(self, chunk, repl_chunk, new_region, chunk_x, chunk_z):
        new_chunk = 0
        x = 0
        y = 0
        z = 0

        # Create `Block` objects that are used to set blocks
        stone = anvil.Block('minecraft', 'stone')
        water = anvil.Block('minecraft', 'water')
        diamond_block = anvil.Block('minecraft', 'diamond_block')
        gold_block = anvil.Block('minecraft', 'gold_block')
        blue_wool = anvil.Block('minecraft', 'blue_wool')

        # Iterate all blocks and select write the new block to the new_chunk
        for block in chunk.stream_chunk():
            b = block

            x_region = chunk_x * cfg.CHUNK_B_X + x
            z_region = chunk_z * cfg.CHUNK_B_Z + z
            x_global = new_region.x * cfg.REGION_B_X + x_region
            z_global = new_region.z * cfg.REGION_B_Z + z_region

            xyz = self.identifier.identified[x_region, y, z_region]
            if xyz == cfg.WATERBLOCK:
                b = water
                print(f'Found water Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            elif xyz == cfg.AIRPOCKET:
                if repl_chunk:
                    b = self.get_replacement_block(repl_chunk, x, y, z)
                else:
                    b = stone
                print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            elif xyz == cfg.SOLIDAREA:
                if repl_chunk:
                    b = self.get_replacement_block(repl_chunk, x, y, z)
                # b = self.get_replacement_block(repl_chunk, x, y, z)
                if repl_chunk:
                    new_block = repl_chunk.get_block(x, y, z)
                    # Replace the block if it is solid but use the original when it is not
                    if is_solid(new_block.id):
                        b = new_block
                    # TODO debug version
                    b = diamond_block
            elif xyz != cfg.UNCHANGED:
                print(f'Found unidentified Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z}) with {xyz}, this should not happen')
                print(f'GlobalPos: ({x_global}, {y}, {z_global})')

            try:
                new_chunk = new_region.set_block(b, x_global, y, z_global)
            except:
                print(f'could not set Block ({x},{y},{z})')

            # TODO
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        new_chunk.set_data(chunk.data)

    def get_replacement_block(self, repl_chunk, x, y, z):
        gold_block = anvil.Block('minecraft', 'gold_block')

        b = gold_block
        # if repl_chunk:
        #     new_block = repl_chunk.get_block(x, y, z)
        #     # TODO expand is_solid list
        #     if is_solid(new_block.id):
        #         b = new_block
        #         b = blue_wool

        return b
