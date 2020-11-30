# minecraft import
import anvil

# Needed for the file iteration
import os

# For array manipulations
import numpy as np

from tkinter import END
# TODO
from tkinter import messagebox

from block_tests import is_air, is_water, is_transparent, is_solid

# utilities
from math import floor
# TODO
import time
import datetime
from time import gmtime, strftime

###################################################################################################
# VERSION 1.0
###################################################################################################

###################################################################################################
# Checks
###################################################################################################
# TODO add range parameter
def check_neighbours_validator(chunk, x, y, z, validator, amount = 1):
    if (x <= 0 or y <= 0 or z <= 0
        or x >= 15 or y >= 255 or z >= 15):
        return False

    for i in range(x - amount, x + amount + 1):
        for j in range(y - amount, y + amount + 1):
            for k in range(z - amount, z + amount + 1):
                if not (x == i and y == j and z == k):
                    block = chunk.get_block(i, j, k)
                    if validator(block.id):
                        return False
    return True

# TODO this should be a pocket search similar to how the air pockets should be found
# TODO the marking mechanism does not work because the stateArray is only changed for one block
def checkWaterBlocks(chunk, block, x, y, z):
    if is_solid(block.id):
        return check_neighbours_validator(chunk, x, y, z, lambda s: not is_water(s))
    return False

def checkAirPockets(chunk, block, x, y, z):
    if is_air(block.id):
        return check_neighbours_validator(chunk, x, y, z, lambda s: is_transparent(s) or is_water(s))
    return False

def checkSolidArea(chunk, block, x, y, z):
    # TODO what about water? is it in transparent blocks? + lava
    if is_solid(block.id):
        return check_neighbours_validator(chunk, x, y, z, lambda s: is_transparent(s) or is_water(s))
    return False

###################################################################################################
# Copy
###################################################################################################
def copyChunkOld(newRegion, region, replRegion,
    chunkX, chunkZ,
    water_blocks, air_pockets, solid_blocks):

    global changeCountWater
    global changeCountAir
    global changeCountSolid

    chunk = None
    try:
        chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
    except:
        print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

    if chunk:
        replChunk = False
        if replRegion:
            try:
                replChunk = anvil.Chunk.from_region(replRegion, chunkX, chunkZ)
            except:
                print(f'Could not create replacement chunk for {chunkX}, {chunkZ}.')

        # print(replRegion, replChunk)

        # Init
        stateArray = np.zeros((16, 256, 16), dtype=int)
        x = 0
        y = 0
        z = 0

        # TODO position that is altered but shouldnt be
        # (230, 31, 164)
        # (228, 31, 167)

        #  For debugging : block position
        # if x == 13 and y == 50 and z == 10:
        # Check how the chunk should be modified and save it in the stateArray
        for block in chunk.stream_chunk():
            if stateArray[x, y, z] == UNCHECKED:
                if water_blocks == 1 and checkWaterBlocks(chunk, block, x, y, z):
                    stateArray[x, y, z] = WATERBLOCK
                    changeCountWater += 1
                elif air_pockets == 1 and checkAirPockets(chunk, block, x, y, z):
                    if solid_blocks == 1:
                        stateArray[x, y, z] = AIRPOCKET
                    else:
                        stateArray[x, y, z] = AIRPOCKET_STONE
                    changeCountAir += 1
                elif solid_blocks == 1 and checkSolidArea(chunk, block, x, y, z):
                    stateArray[x, y, z] = SOLIDAREA
                    changeCountSolid += 1
                else:
                    stateArray[x, y, z] = UNCHANGED

            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        # Reset
        newChunk = 0
        x = 0
        y = 0
        z = 0

        # Create `Block` objects that are used to set blocks
        stone = anvil.Block('minecraft', 'stone')
        water = anvil.Block('minecraft', 'water')
        diamond_block = anvil.Block('minecraft', 'diamond_block')
        gold_block = anvil.Block('minecraft', 'gold_block')

        # Iterate all blocks and select write the new block to the newChunk
        for block in chunk.stream_chunk():
            b = block

            # TODO if air block and not replacement igrnore?

            xyz = stateArray[x, y, z]
            if xyz == WATERBLOCK:
                b = water
                print(f'Found water Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz == AIRPOCKET:
                b = stone
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    if is_solid(newBlock.id):
                        b = newBlock
                print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz == AIRPOCKET_STONE:
                b = gold_block
                print(f'Found AIRPOCKET_STONE Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz == SOLIDAREA:
                b = stone
                if replChunk:
                    newBlock = replChunk.get_block(x, y, z)
                    if is_solid(newBlock.id):
                        # b = newBlock
                        # TODO debug version
                        b = diamond_block
            elif xyz == UNCHECKED:
                print(f'Found unchecked Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                #print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif xyz != UNCHANGED:
                print(f'Found unidentified Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}) with {stateArray[x, y, z]}, this should not happen')
                #print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')

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

###################################################################################################
# VERSION 2.0
###################################################################################################

###################################################################################################
# Checks
###################################################################################################
def check_neighbours_validator2(state_array, x, y, z, validator, amount = 1):
    if (x <= 0 or y <= 0 or z <= 0
        or x >= 15 or y >= 255 or z >= 15):
        return False

    for i in range(x - amount, x + amount + 1):
        for j in range(y - amount, y + amount + 1):
            for k in range(z - amount, z + amount + 1):
                if not (x == i and y == j and z == k):
                    if validator(state_array[i, j, k]):
                       return False
    return True

def check_water_blocks(state_array, x, y, z):
    if state_array[x, y, z] == G_SOLID:
        return check_neighbours_validator2(state_array, x, y, z, lambda s: s != G_WATER)
    return False

def check_air_pockets(state_array, x, y, z):
    if state_array[x, y, z] == G_AIR:
        return check_neighbours_validator2(state_array, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
    return False

def check_solid_area(state_array, x, y, z):
    # TODO what about water? is it in transparent blocks? + lava
    if state_array[x, y, z] == G_SOLID:
        return check_neighbours_validator2(state_array, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
    return False

###################################################################################################
# Copy
###################################################################################################
UNCHECKED = 0
UNCHANGED = 1
WATERBLOCK = 2
AIRPOCKET = 3
AIRPOCKET_STONE = 4
SOLIDAREA = 5

G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

changeCountWater = 0
changeCountAir = 0
changeCountSolid = 0

def classify(chunk, state_array):
    x = 0
    y = 0
    z = 0
    for block in chunk.stream_chunk():
        if is_air(block.id):
            state_array[x, y, z] = G_AIR
        elif is_water(block.id):
            state_array[x, y, z] = G_WATER
        elif is_transparent(block.id):
            state_array[x, y, z] = G_TRANSPARENT
        else:
            state_array[x, y, z] = G_SOLID

        if z == 15 and x == 15:
            y += 1
        if x == 15:
            z = (z + 1) % 16
        x = (x + 1) % 16

def identify(chunk, state_array, state_array2, water_blocks, air_pockets, solid_blocks):
    global changeCountWater
    global changeCountAir
    global changeCountSolid

    x = 0
    y = 0
    z = 0
    for block in chunk.stream_chunk():
        if water_blocks == 1 and check_water_blocks(state_array, x, y, z):
            state_array2[x, y, z] = WATERBLOCK
            changeCountWater += 1
        elif air_pockets == 1 and check_air_pockets(state_array, x, y, z):
            if solid_blocks == 1:
                state_array2[x, y, z] = AIRPOCKET
            else:
                state_array2[x, y, z] = AIRPOCKET_STONE
            changeCountAir += 1
        elif solid_blocks == 1 and check_solid_area(state_array, x, y, z):
            state_array2[x, y, z] = SOLIDAREA
            changeCountSolid += 1
        else:
            state_array2[x, y, z] = UNCHANGED

        if z == 15 and x == 15:
            y += 1
        if x == 15:
            z = (z + 1) % 16
        x = (x + 1) % 16

def modify(state_array, chunk, replChunk, newRegion, chunkX, chunkZ):
    newChunk = 0
    x = 0
    y = 0
    z = 0

    # Create `Block` objects that are used to set blocks
    stone = anvil.Block('minecraft', 'stone')
    water = anvil.Block('minecraft', 'water')
    diamond_block = anvil.Block('minecraft', 'diamond_block')
    gold_block = anvil.Block('minecraft', 'gold_block')

    # Iterate all blocks and select write the new block to the newChunk
    for block in chunk.stream_chunk():
        b = block

        # TODO if air block and not replacement igrnore?
        xyz = state_array[x, y, z]
        if xyz == WATERBLOCK:
            b = water
            print(f'Found water Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
            print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
        # TODO combine airpocket and airpocket_stone
        elif xyz == AIRPOCKET:
            if replChunk:
                newBlock = replChunk.get_block(x, y, z)
                if is_solid(newBlock.id):
                    b = newBlock
            else:
                b = gold_block
            print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
            print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
        elif xyz == AIRPOCKET_STONE:
            b = gold_block
            print(f'Found AIRPOCKET_STONE Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ})')
            print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
        elif xyz == SOLIDAREA:
            b = stone
            if replChunk:
                newBlock = replChunk.get_block(x, y, z)
                if is_solid(newBlock.id):
                    # b = newBlock
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

def copyChunk(newRegion, region, replRegion,
    chunkX, chunkZ,
    water_blocks, air_pockets, solid_blocks):

    global changeCountWater
    global changeCountAir
    global changeCountSolid

    chunk = None
    try:
        chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
    except:
        print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

    if chunk:

        # ms = int(round(time.time() * 1000))

        classified = np.zeros((16, 256, 16), dtype=int)
        classify(chunk, classified)

        # ms2 = int(round(time.time() * 1000))
        # print(ms2 - ms)
        # ms = int(round(time.time() * 1000))

        identified = np.zeros((16, 256, 16), dtype=int)
        identify(chunk, classified, identified, water_blocks, air_pockets, solid_blocks)

        # ms2 = int(round(time.time() * 1000))
        # print(ms2 - ms)
        # ms = int(round(time.time() * 1000))

        # TODO only when the option is tikced?
        replChunk = False
        if replRegion:
            try:
                replChunk = anvil.Chunk.from_region(replRegion, chunkX, chunkZ)
            except:
                print(f'Could not create replacement chunk for {chunkX}, {chunkZ}.')

        modify(identified, chunk, replChunk, newRegion, chunkX, chunkZ)

        # ms2 = int(round(time.time() * 1000))
        # print(ms2 - ms)

###################################################################################################

def copyRegion(meta_info, filename):

    src_dir = meta_info.source_dir.get()
    target_dir = meta_info.target_dir.get()
    repl_dir = meta_info.replacement_dir.get()

    water_blocks = meta_info.water_blocks.get()
    air_pockets = meta_info.air_pockets.get()
    solid_blocks = meta_info.repl_blocks.get()

    l = filename.split('.')
    rX = int(l[1])
    rZ = int(l[2])

    # Create a new region with the `EmptyRegion` class at region coords
    newRegion = anvil.EmptyRegion(rX, rZ)
    region = anvil.Region.from_file(src_dir + "/" + filename)

    replRegion = False
    if solid_blocks:
        try:
            replRegion = anvil.Region.from_file(repl_dir + "/" + filename)
        except:
            print(f'Could not create replacement region for {filename}.')

    # max_chunkX = 1
    # max_chunkZ = 1
    max_chunkX = 32
    max_chunkZ = 32
    meta_info.chunk_count_max = max_chunkX * max_chunkZ

    for chunkX in range(max_chunkX):
    # for chunkX in range(13, 15):

        for chunkZ in range(max_chunkZ):
        # for chunkZ in range(7, 11):

            # copyChunkOld(newRegion, region, replRegion, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks)
            copyChunk(newRegion, region, replRegion, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks)

            meta_info.chunk_count = chunkZ + 1 + chunkX * max_chunkZ

    # TODO changeCountAir is not reset OBACHT global var
    if water_blocks + air_pockets + solid_blocks >= 1:
        meta_info.text_queue.put(f'In file {filename}:\n')
    if water_blocks == 1:
        meta_info.text_queue.put(f'Changed {changeCountWater} solid blocks to water.\n')
    if air_pockets == 1:
        meta_info.text_queue.put(f'Changed {changeCountAir} air blocks to solid blocks.\n')
    if solid_blocks == 1:
        meta_info.text_queue.put(f'Changed {changeCountSolid} solid blocks to replacement solid blocks.\n')

    # Save to a file
    newRegion.save(target_dir + "/" + filename)

###################################################################################################
# Main
###################################################################################################
def run(meta_info):

    # Print detailed informations
    if (meta_info.water_blocks.get() == 1):
        meta_info.text_queue.put("Water Blocks will be fixed!\n")
    else:
        meta_info.text_queue.put("Water Blocks will not be fixed!\n")

    if (meta_info.air_pockets.get() == 1):
        meta_info.text_queue.put("Air Blocks will be fixed!\n")
    else:
        meta_info.text_queue.put("Air Blocks will not be fixed!\n")

    if (meta_info.repl_blocks.get() == 1):
        meta_info.text_queue.put("Replacement Blocks will be inserted!\n")
    else:
        meta_info.text_queue.put("Replacement Blocks will not be inserted!\n")

    meta_info.text_queue.put("\n.. starting\n")
    t1 = gmtime()
    meta_info.text_queue.put(strftime("%Y-%m-%d %H:%M:%S\n", t1))
    ms = int(round(time.time() * 1000))

    # Get all files in the directory
    filelist = os.listdir(meta_info.source_dir.get())
    if len(filelist) == 0:
        messagebox.showinfo(message="No files found! Select a different source path.", title = "Error")
        return

    tgt_dir = meta_info.target_dir.get()
    try:
        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)
    except OSError:
        messagebox.showinfo(message="Creation of the directory %s failed" % tgt_dir, title = "Error")

    # Update the progressbar and label for the files
    meta_info.file_count_max = len(filelist)

    # Iterate the files
    i = 1
    for filename in filelist:
        if filename.endswith(".mca"):
            copyRegion(meta_info, filename)
        else:
            continue
        meta_info.file_count = i
        i += 1

    # Print that the process is finished
    meta_info.text_queue.put("\n.. finished\n")
    t2 = gmtime()
    meta_info.text_queue.put(strftime("%Y-%m-%d %H:%M:%S\n", t2))
    meta_info.text_queue.put("Total runtime: ")
    meta_info.text_queue.put(datetime.timedelta(seconds=time.mktime(t2)-time.mktime(t1)))

    ms2 = int(round(time.time() * 1000))
    print(f"Total time elapsed: {ms2 - ms}")

    meta_info.finished = True

import queue
def runloop(meta_info):
    result = 0

    max = 10000000
    # meta_info.file_progress["maximum"] = max
    # meta_info.chunk_progress["maximum"] = max
    meta_info.chunk_count_max = max
    meta_info.file_count_max = max

    print(meta_info.source_dir.get())
    print(meta_info.replacement_dir.get())
    print(meta_info.target_dir.get())

    for i in range(max):
        #Do something with result
        result = result + 1

        meta_info.chunk_count = result
        meta_info.file_count = result
        # if (i % 1000):
        #     meta_info.text_queue.put("Hi\n")
        # meta_info.file_count = result
        # meta_info.chunk_progress["value"] = result
        # meta_info.file_progress["value"] = result




    meta_info.finished = True
