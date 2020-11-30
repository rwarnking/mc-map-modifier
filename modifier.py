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
# Update method
###################################################################################################
def updateProgressBar(progress, value):
    progress['value'] = value
    progress.update()

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
        return check_neighbours_validator(chunk, x, y, z, is_transparent)
    return False

def checkSolidArea(chunk, block, x, y, z):
    # TODO what about water? is it in transparent blocks? + lava
    if is_solid(block.id):
        return check_neighbours_validator(chunk, x, y, z, is_transparent)
    return False
















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

        state_array = np.zeros((16, 256, 16), dtype=int)
        classify(chunk, state_array)

        # ms2 = int(round(time.time() * 1000))
        # print(ms2 - ms)
        # ms = int(round(time.time() * 1000))

        state_array2 = np.zeros((16, 256, 16), dtype=int)
        identify(chunk, state_array, state_array2, water_blocks, air_pockets, solid_blocks)

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

        modify(state_array2, chunk, replChunk, newRegion, chunkX, chunkZ)

        # ms2 = int(round(time.time() * 1000))
        # print(ms2 - ms)


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

def copyRegion(chunk_progress, chunk_label, details_text,
    src_dir, target_dir, repl_dir, filename,
    water_blocks, air_pockets, solid_blocks):

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

    max_chunkX = 1
    max_chunkZ = 1
    # max_chunkX = 32
    # max_chunkZ = 32
    chunk_progress["maximum"] = max_chunkX * max_chunkZ
    chunk_label.config(text=f"Finished chunk 0, 0 of {max_chunkX - 1}, {max_chunkZ - 1}. And 0 of {max_chunkX * max_chunkZ} chunks.")

    # for debugging
    #for chunkX in range(4, max_chunkX):
    #    for chunkZ in range(25, max_chunkZ):


    for chunkX in range(max_chunkX):
    # for chunkX in range(13, 15):

        # TODO
        # import concurrent.futures
        # executor = concurrent.futures.ProcessPoolExecutor(10)
        # futures = [executor.submit(copyChunk, newRegion, region, replRegion, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks) for chunkZ in range(max_chunkZ)]
        # concurrent.futures.wait(futures)

        for chunkZ in range(max_chunkZ):
        # for chunkZ in range(9, 11):

            copyChunkOld(newRegion, region, replRegion, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks)

            updateProgressBar(chunk_progress, chunkZ + 1 + chunkX * max_chunkZ)
            chunk_label.config(text=f"Finished chunk {chunkX}, {chunkZ} of {max_chunkX - 1}, {max_chunkZ - 1}. And {chunkZ + 1 + chunkX * max_chunkZ} of {max_chunkX * max_chunkZ} chunks.")

    #from thread import start_new_thread
    #start_new_thread(heron,(99,))

    # TODO changeCountAir is not reset OBACHT global var
    if water_blocks + air_pockets + solid_blocks >= 1:
        details_text.insert(END, f'In file {filename}:\n')
    if water_blocks == 1:
        details_text.insert(END, f'Changed {changeCountWater} solid blocks to water.\n')
    if air_pockets == 1:
        details_text.insert(END, f'Changed {changeCountAir} air blocks to solid blocks.\n')
    if solid_blocks == 1:
        details_text.insert(END, f'Changed {changeCountSolid} solid blocks to replacement solid blocks.\n')

    # Save to a file
    newRegion.save(target_dir + "/" + filename)

###################################################################################################
# Main
###################################################################################################
def run(src_dir, tgt_dir, repl_dir,
    chunk_progress, file_progress,
    chunk_label, files_label,
    water_blocks, air_pockets, solid_blocks,
    details_text):

    # Print detailed informations
    if (water_blocks == 1):
        details_text.insert(END, "Water Blocks will be fixed!\n")
    else:
        details_text.insert(END, "Water Blocks will not be fixed!\n")

    if (air_pockets == 1):
        details_text.insert(END, "Air Blocks will be fixed!\n")
    else:
        details_text.insert(END, "Air Blocks will not be fixed!\n")

    if (solid_blocks == 1):
        details_text.insert(END, "Replacement Blocks will be inserted!\n")
    else:
        details_text.insert(END, "Replacement Blocks will not be inserted!\n")

    details_text.insert(END, "\n.. starting\n")
    t1 = gmtime()
    details_text.insert(END, strftime("%Y-%m-%d %H:%M:%S\n", t1))
    ms = int(round(time.time() * 1000))

    # Get all files in the directory
    filelist = os.listdir(src_dir)
    if len(filelist) == 0:
        messagebox.showinfo(message="No files found! Select a different source path.", title = "Error")
        return

    try:
        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)
    except OSError:
        messagebox.showinfo(message="Creation of the directory %s failed" % tgt_dir, title = "Error")

    # Update the progressbar and label for the files
    file_progress["maximum"] = len(filelist)
    files_label.config(text=f"Finished file {0} of {len(filelist)} files.")

    # Iterate the files
    i = 1
    for filename in filelist:
        if filename.endswith(".mca"):
            copyRegion(chunk_progress, chunk_label, details_text,
                src_dir, tgt_dir, repl_dir, filename,
                water_blocks, air_pockets, solid_blocks)
        else:
            continue
        updateProgressBar(file_progress, i)
        files_label.config(text=f"Finished file {i} of {len(filelist)} files.")
        i += 1

    # Print that the process is finished
    details_text.insert(END, "\n.. finished\n")
    t2 = gmtime()
    details_text.insert(END, strftime("%Y-%m-%d %H:%M:%S\n", t2))
    details_text.insert(END, "Total runtime: ")
    details_text.insert(END, datetime.timedelta(seconds=time.mktime(t2)-time.mktime(t1)))


    ms2 = int(round(time.time() * 1000))
    print(ms2 - ms)
