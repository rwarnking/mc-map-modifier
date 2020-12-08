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
from classifier import Classifier
from identifier import Identifier
from classifier_mp_mt import ClassifierMPMT
from block_tests import is_solid, get_type

UNCHECKED = 0
UNCHANGED = 1
UNCHANGED2 = 0
WATERBLOCK = 2
AIRPOCKET = 3
SOLIDAREA = 4

G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

class Modifier():
    def __init__(self, meta_info):
        self.meta_info = meta_info

        self.max_chunkX = 32
        self.max_chunkZ = 32

        self.changeCountWater = 0
        self.changeCountAir = 0
        self.changeCountRepl = 0

        # TODO
        self.max_chunk_x = 32
        self.max_chunk_z = 32

        self.block_size_x = 16
        self.block_size_y = 256
        self.block_size_z = 16

        self.size_x = self.max_chunk_x * self.block_size_x
        self.size_y = 256
        self.size_z = self.max_chunk_z * self.block_size_z

    ###############################################################################################
    # Checks
    ###############################################################################################
    def check_neighbours_v(self, states, x, y, z, validator, amount = 1):
        if (x <= 0 or y <= 0 or z <= 0
            or x >= 15 or y >= 255 or z >= 15):
            return False

        for i in range(x - amount, x + amount + 1):
            for j in range(y - amount, y + amount + 1):
                for k in range(z - amount, z + amount + 1):
                    if not (x == i and y == j and z == k):
                        if validator(states[i, j, k]):
                            return False
        return True

    def check_neighbours_v_2(self, states, x, y, z, validator, limit = 1, amount = 1):
        if (x <= 0 or y <= 0 or z <= 0
            or x >= 15 or y >= 255 or z >= 15):
            return False

        neighbour = True

        for i in range(x - amount, x + amount + 1):
            for j in range(y - amount, y + amount + 1):
                for k in range(z - amount, z + amount + 1):
                    if not (x == i and y == j and z == k):
                        if validator(states[i, j, k]):
                            if neighbour == True:
                                neighbour = [i, j, k]
                            else:
                                return False

        return neighbour

    def check_water_blocks(self, wp_size, states, x, y, z):
        if states[x, y, z] == G_SOLID:
            if wp_size == 1:
                return self.check_neighbours_v(states, x, y, z, lambda s: s != G_WATER)
            # TODO this is kinda stupid because for every block the 2-case applies, the test is run
            # instead mark all blocks that are processed here
            elif wp_size == 2:
                res = self.check_neighbours_v_2(states, x, y, z, lambda s: s != G_WATER)
                if isinstance(res, bool):
                    return res
                res = self.check_neighbours_v_2(states, res[0], res[1], res[2], lambda s: s != G_WATER)
                return res != False
            else:
                return self.check_neighbours_v(states, x, y, z, lambda s: s != G_WATER)
        return False

    def check_air_pockets(self, states, x, y, z):
        if states[x, y, z] == G_AIR:
            return self.check_neighbours_v(states, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
        return False

    def check_solid_area(self, states, x, y, z):
        # TODO what about water? is it in transparent blocks? + lava
        if states[x, y, z] == G_SOLID:
            return self.check_neighbours_v(states, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
        return False

    ###############################################################################################
    # Copy
    ###############################################################################################
    def classify(self, chunk, classified):
        x = 0
        y = 0
        z = 0

        for block in chunk.stream_chunk():
            classified[x, y, z] = get_type(block.id)

            # TODO self.blocks_chunk_x
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

    def identify(self, chunk, states, new_states):
        wp_size = int(self.meta_info.wpocket_size.get())

        x = 0
        y = 0
        z = 0
        for block in chunk.stream_chunk():
            if self.water_blocks == 1 and self.check_water_blocks(wp_size, states, x, y, z):
                new_states[x, y, z] = WATERBLOCK
                self.changeCountWater += 1
            elif self.air_pockets == 1 and self.check_air_pockets(states, x, y, z):
                new_states[x, y, z] = AIRPOCKET
                self.changeCountAir += 1
            elif self.repl_blocks == 1 and self.check_solid_area(states, x, y, z):
                new_states[x, y, z] = SOLIDAREA
                self.changeCountRepl += 1
            else:
                new_states[x, y, z] = UNCHANGED

            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

    def modify(self, states, chunk, replChunk, newRegion, chunkX, chunkZ):
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

            xyz = states[x, y, z]
            if xyz == WATERBLOCK:
                b = water
                print(f'Found water Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz == AIRPOCKET:
                b = gold_block
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    # TODO expand is_solid list
                    if is_solid(newBlock.id):
                        b = newBlock
                        b = blue_wool
                print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz == SOLIDAREA:
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    # Replace the block if it is solid but use the original when it is not
                    if is_solid(newBlock.id):
                        b = newBlock
                        # TODO debug version
                        b = diamond_block
            elif xyz == UNCHECKED:
                print(f'Found unchecked Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                #print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz != UNCHANGED:
                print(f'Found unidentified Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}) with {stateArray[x, y, z]}, this should not happen')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')

            try:
                newChunk = newRegion.set_block(b, newRegion.x * 512 + chunkX * 16 + x, y, newRegion.z * 512 + chunkZ * 16 + z)
            except:
                print(f'could not set Block ({x},{y},{z})')

            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        newChunk.set_data(chunk.data)



    def modify2(self, chunk, replChunk, newRegion, chunkX, chunkZ):
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

            x_region = chunkX * 16 + x
            z_region = chunkZ * 16 + z
            x_global = newRegion.x * 512 + x_region
            z_global = newRegion.z * 512 + z_region

            xyz = self.identifier.identified[x_region, y, z_region]
            # if xyz == WATERBLOCK:
            #     b = water
            #     print(f'Found water Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
            #     print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            # elif xyz == AIRPOCKET:
            #     b = gold_block
            #     if replChunk:
            #         newBlock = replChunk.get_block(x, y, z)
            #         # TODO expand is_solid list
            #         if is_solid(newBlock.id):
            #             b = newBlock
            #             b = blue_wool
            #     print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
            #     print(f'GlobalPos: ({x_global}, {y}, {z_global})')
            # elif xyz == SOLIDAREA:
            if xyz == SOLIDAREA:
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    # Replace the block if it is solid but use the original when it is not
                    if is_solid(newBlock.id):
                        b = newBlock
                    # TODO debug version
                    b = diamond_block
            # elif xyz == UNCHECKED:
            #     print(f'Found unchecked Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                #print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz != UNCHANGED2:
                print(f'Found unidentified Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}) with {xyz}, this should not happen')
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

    def copy_chunk_1(self, newRegion, region, replRegion, chunkX, chunkZ):
        chunk = None
        try:
            chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
        except:
            print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

        if chunk:
            classified = np.zeros((16, 256, 16), dtype=int)
            self.classify(chunk, classified)

            identified = np.zeros((16, 256, 16), dtype=int)
            self.identify(chunk, classified, identified)

            # TODO only when the option is tikced?
            replChunk = False
            if replRegion:
                try:
                    replChunk = anvil.Chunk.from_region(replRegion, chunkX, chunkZ)
                except:
                    print(f'Could not create replacement chunk for {chunkX}, {chunkZ}.')

            self.modify(identified, chunk, replChunk, newRegion, chunkX, chunkZ)


    def copy_chunk_2(self, newRegion, region, replRegion, chunkX, chunkZ):
        chunk = None
        try:
            chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
        except:
            print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

        if chunk:
            self.classifier.classify_one(chunk, chunkX, chunkZ)
            self.classified_region = self.classifier.classified_region

            self.changeCountWater, self.changeCountAir, self.changeCountRepl = self.identifier.identify(chunk, self.classified_region, chunkX, chunkZ)
            identified = self.identifier.identified

            # TODO only when the option is ticked?
            replChunk = False
            if replRegion:
                try:
                    replChunk = anvil.Chunk.from_region(replRegion, chunkX, chunkZ)
                except:
                    print(f'Could not create replacement chunk for {chunkX}, {chunkZ}.')

            self.modify(identified, chunk, replChunk, newRegion, chunkX, chunkZ)


    def copy_chunk_3(self, newRegion, region, replRegion, chunkX, chunkZ):
        chunk = None
        try:
            chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
        except:
            print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

        if chunk:
            self.changeCountWater, self.changeCountAir, self.changeCountRepl = self.identifier.identify(chunk, self.classified_region, chunkX, chunkZ)
            identified = self.identifier.identified

            # TODO only when the option is ticked?
            replChunk = False
            if replRegion:
                try:
                    replChunk = anvil.Chunk.from_region(replRegion, chunkX, chunkZ)
                except:
                    print(f'Could not create replacement chunk for {chunkX}, {chunkZ}.')

            self.modify(identified, chunk, replChunk, newRegion, chunkX, chunkZ)




    def copy_chunk_4(self, new_region, region, repl_region, chunk_x, chunk_z):
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

            self.modify2(chunk, repl_chunk, new_region, chunk_x, chunk_z)

    ###############################################################################################

    def copy_chunks_1(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32
        # for chunkX in range(max_chunkX):
        for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            # for chunkZ in range(max_chunkZ):
            for chunkZ in range(11, 16):
                self.copy_chunk_1(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk


    def copy_chunks_2(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32
        self.classifier = Classifier()
        self.identifier = Identifier(self.meta_info)

        # for chunkX in range(max_chunkX):
        for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            # for chunkZ in range(max_chunkZ):
            for chunkZ in range(11, 16):
                self.copy_chunk_2(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk

    def copy_chunks_3(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32
        classifier = Classifier(True)
        classifier.classify_all(region)
        self.classified_region = classifier.classified_region
        # print(classifier.classified_region[0,0,0])

        # for i in range(self.size_x):
        #     for j in range(self.size_y):
        #         for k in range(self.size_z):
        #             if classifier.classified_region[i,j,k] > 0:
        #                 print("hi")
        # np.savetxt('data.csv', self.classified_region[0], delimiter=',')

        self.identifier = Identifier(self.meta_info, True)

        # for chunkX in range(max_chunkX):
        for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            # for chunkZ in range(max_chunkZ):
            for chunkZ in range(11, 16):
                self.copy_chunk_3(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk

    def copy_chunks_4(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32

        classifier_mp_mt = ClassifierMPMT()
        classifier_mp_mt.classify_all_mp(region)
        self.classified_region = classifier_mp_mt.classified_region

        self.identifier = Identifier(self.meta_info, True)

        # for chunkX in range(max_chunkX):
        for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            # for chunkZ in range(max_chunkZ):
            for chunkZ in range(11, 16):
                self.copy_chunk_3(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk

    def copy_chunks_5(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32

        classifier_mp_mt = ClassifierMPMT()
        classifier_mp_mt.classify_all_mt(region)
        self.classified_region = classifier_mp_mt.classified_region

        self.identifier = Identifier(self.meta_info, True)

        # for chunkX in range(max_chunkX):
        for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            # for chunkZ in range(max_chunkZ):
            for chunkZ in range(11, 16):
                self.copy_chunk_3(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

            ms2 = int(round(time.time() * 1000))
            self.meta_info.elapsed_time += (ms2 - ms) / 1000
            t_per_chunk = self.meta_info.elapsed_time / (self.meta_info.chunk_count_max * self.meta_info.file_count + self.meta_info.chunk_count)
            self.meta_info.estimated_time = ((self.meta_info.chunk_count_max - self.meta_info.chunk_count) \
                + (self.meta_info.file_count_max - self.meta_info.file_count - 1) * self.meta_info.chunk_count_max) * t_per_chunk

    def copy_chunks_6(self, newRegion, region, replRegion):
        # TODO
        max_chunkX = 32
        max_chunkZ = 32

        ms = int(round(time.time() * 1000))

        classifier_mp_mt = ClassifierMPMT()
        classifier_mp_mt.classify_all_mp(region)
        self.classified_region = classifier_mp_mt.classified_region

        ms2 = int(round(time.time() * 1000))
        print(f"Classifier time: {ms2 - ms}")

        self.identifier = Identifier(self.meta_info, True)
        # TODO names
        self.changeCountWater, self.changeCountAir, self.changeCountRepl = self.identifier.identify_label(self.classified_region)

        ms3 = int(round(time.time() * 1000))
        print(f"Identifier time: {ms3 - ms2}")

        for chunkX in range(max_chunkX):
        # for chunkX in range(10, 12):

            ms = int(round(time.time() * 1000))
            for chunkZ in range(max_chunkZ):
            # for chunkZ in range(11, 16):
                self.copy_chunk_4(newRegion, region, replRegion, chunkX, chunkZ)
                self.meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

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

        # max_chunkX = 1
        # max_chunkZ = 1
        # TODO self?
        max_chunkX = 32
        max_chunkZ = 32
        self.meta_info.chunk_count = 0
        self.meta_info.chunk_count_max = max_chunkX * max_chunkZ
        self.meta_info.estimated_time = self.meta_info.chunk_count_max * self.meta_info.file_count_max

##########################################

        # some chunks, one class, no write. time:
        # 15344, 15454, 15426, 14826, 15127
        # self.copy_chunks_1(newRegion, region, replRegion)

        # some chunks, multiple classes, no write. time:
        # 15437, 15678, 16431, 15245, 15107
        # self.copy_chunks_2(newRegion, region, replRegion)

        # some chunks, multiple classes, no write, one classifier array. time:
        # 16963, 17202, 17311, 17044, 17307, 17436
        # self.copy_chunks_3(newRegion, region, replRegion)

        # some chunks, multiple classes, no write, one classifier array, multiprocessing. time:
        # 61477, 64481, 61016
        # self.copy_chunks_4(newRegion, region, replRegion)

        # some chunks, multiple classes, no write, one classifier array, multithreading. time:
        # 146684
        # self.copy_chunks_5(newRegion, region, replRegion)

        self.copy_chunks_6(newRegion, region, replRegion)

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
