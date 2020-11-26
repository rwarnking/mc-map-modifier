# minecraft import
import anvil

# Needed for the file iteration
import os

# For array manipulations
import numpy as np

from tkinter import END
# TODO
from tkinter import messagebox

# utilities
from math import floor
from time import gmtime, strftime

def getBlockFromGPos(blockX, blockY, blockZ):
    blockXinChunk = blockX % 16
    blockZinChunk = blockZ % 16

    chunkX = floor(blockX / 16)
    chunkZ = floor(blockZ / 16)
    regionX = floor(chunkX / 32.0)
    regionZ = floor(chunkZ / 32.0)

    path = 'original/'
    filename = 'r.'+str(regionX)+'.'+str(regionZ)+'.mca'
    region = anvil.Region.from_file(path + filename)

    # You can also provide the region file name instead of the object
    chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)

    # If `section` is not provided, will get it from the y coords
    # and assume it's global
    block = chunk.get_block(blockXinChunk, blockY, blockZinChunk)
    return block


def printRegion(filename):

    region = anvil.Region.from_file(filename)
    chunks = 0
    chunkSum = 0

    for chunkX in range(32):
        for chunkZ in range(32):

            try:
                chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
                chunks += 1
            except:
                chunkSum += 1
                # print(f'did not find chunk ({chunkX},{chunkZ})')

    print(f'found {chunks} chunks')


# block = getBlockFromGPos(170, 76, 209)
# print(block) # <Block(minecraft:air)>
# print(block.id) # air
# print(block.properties) # {}


# print('.. starting')
# print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
# # copyRegion(0, 0)
# # printRegion('r.0.0.mca')
# print('.. finished')
# print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))







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
def checkNeighbours(chunk, x, y, z, blockType):
    if (x <= 0 or y <= 0 or z <= 0
        or x >= 15 or y >= 255 or z >= 15):
        return False

    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            for k in range(z - 1, z + 2):
                if not (x == i and y == j and z == k):
                    block = chunk.get_block(i, j, k)
                    if block.id == blockType:
                        return False
    return True

# TODO multiple types should be possible
# TODO this should be a pocket search similar to how the air pockets should be found
# TODO the marking mechanism does not work because the stateArray is only changed for one block
def checkWaterBlocks(chunk, block, x, y, z):
    if block.id == 'dirt':
        return checkNeighbours(chunk, x, y, z, 'dirt')
    return False

# TODO
def checkAirPockets(chunk, block, x, y, z):
    if block.id == 'air':
        return checkNeighbours(chunk, x, y, z, 'air')
    return False

# TODO test not only for stone and air
def checkSolidArea(chunk, block, x, y, z):
    if block.id == 'stone':
        return checkNeighbours(chunk, x, y, z, 'air')
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

changeCountWater = 0
changeCountAir = 0
changeCountSolid = 0

def copyChunk(newRegion, region, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks):
    global changeCountWater
    global changeCountAir
    global changeCountSolid
    # TODO make try block smaller
    try:
        chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)

        # Init
        stateArray = np.zeros((16, 256, 16), dtype=int)
        x = 0
        y = 0
        z = 0

        # For debugging : block position
        # if x == 13 and y == 50 and z == 10:

        # Check how the chunk should be modified and save it in the stateArray
        for block in chunk.stream_chunk():
            if stateArray[x, y, z] == UNCHECKED:
                # if water_blocks == 1 and checkWaterBlocks(chunk, block, x, y, z):
                #     stateArray[x, y, z] = WATERBLOCK
                #     changeCountWater += 1
                #print(air_pockets == 1)
                if air_pockets == 1 and checkAirPockets(chunk, block, x, y, z):
                    # if solid_blocks == 1:
                    #     stateArray[x, y, z] = AIRPOCKET
                    # else:
                    stateArray[x, y, z] = AIRPOCKET_STONE
                    changeCountAir += 1
                # elif solid_blocks == 1 and checkSolidArea(chunk, block, x, y, z):
                #     stateArray[x, y, z] = SOLIDAREA
                #     changeCountSolid += 1
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

        # Iterate all blocks and select write the new block to the newChunk
        for block in chunk.stream_chunk():
            b = block

            # TODO if air block and not replacement igrnore?

            if stateArray[x, y, z] == WATERBLOCK:
                b = water
                print(f'Found water Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif stateArray[x, y, z] == AIRPOCKET:
                b = stone
                print(f'Found AIRPOCKET Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
                # TODO
            #     newblock = replChunk.get_block(i, j, k)
            #     if newBlock.id == Solid:
            #         b = newBlock
            #     else:
            #         b = stone
            elif stateArray[x, y, z] == AIRPOCKET_STONE:
                b = stone
                print(f'Found AIRPOCKET_STONE Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should happen')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            # elif stateArray[x, y, z] == SOLIDAREA:
            #     newBlock = replChunk.get_block(i, j, k)
            #     if newBlock.id == Solid:
            #         b = newBlock
            #     else:
            #         b = stone
            elif stateArray[x, y, z] == UNCHECKED:
                print(f'Found unchecked Block ({x},{y},{z}) in Chunk ({chunkX}, {chunkZ}), this should not happen')
                print(f'GlobalPos: ({newRegion.x * 512 + chunkX * 16 + x}, {y}, {newRegion.z * 512 + chunkZ * 16 + z})')
            elif stateArray[x, y, z] != UNCHANGED:
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
    except:
        print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

###################################################################################################

def copyRegion(chunk_progress, chunk_label, details_text,
    src_dir, target_dir, filename,
    water_blocks, air_pockets, solid_blocks):

    l = filename.split('.')
    rX = int(l[1])
    rZ = int(l[2])

    # Create a new region with the `EmptyRegion` class at region coords
    newRegion = anvil.EmptyRegion(rX, rZ)
    region = anvil.Region.from_file(src_dir + "/" + filename)

    max_chunkX = 32
    max_chunkZ = 32
    chunk_progress["maximum"] = max_chunkX * max_chunkZ
    chunk_label.config(text=f"Finished chunk 0, 0 of {max_chunkX - 1}, {max_chunkZ - 1}. And 0 of {max_chunkX * max_chunkZ} chunks.")

    # for debugging
    #for chunkX in range(4, max_chunkX):
    #    for chunkZ in range(25, max_chunkZ):
    for chunkX in range(max_chunkX):
        for chunkZ in range(max_chunkZ):

            copyChunk(newRegion, region, chunkX, chunkZ, water_blocks, air_pockets, solid_blocks)

            updateProgressBar(chunk_progress, chunkZ + 1 + chunkX * max_chunkZ)
            chunk_label.config(text=f"Finished chunk {chunkX}, {chunkZ} of {max_chunkX - 1}, {max_chunkZ - 1}. And {chunkZ + 1 + chunkX * max_chunkZ} of {max_chunkX * max_chunkZ} chunks.")

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
def run(src_dir,
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
        details_text.insert(END, "New Blocks will be fixed!\n")
    else:
        details_text.insert(END, "New Blocks will not be inserted!\n")

    details_text.insert(END, "\n.. starting\n")
    details_text.insert(END, strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    # Get all files in the directory
    filelist = os.listdir(src_dir)
    if len(filelist) == 0:
        messagebox.showinfo(message="No files found! Select a different source path.", title = "Error")
        return

    try:
        target_dir = src_dir + "_copy"
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
    except OSError:
        messagebox.showinfo(message="Creation of the directory %s failed" % target_dir, title = "Error")

    # Update the progressbar and label for the files
    file_progress["maximum"] = len(filelist)
    files_label.config(text=f"Finished file {0} of {len(filelist)} files.")

    # Iterate the files
    i = 1
    for filename in filelist:
        if filename.endswith(".mca"):
            copyRegion(chunk_progress, chunk_label, details_text,
                src_dir, target_dir, filename,
                water_blocks, air_pockets, solid_blocks)
        else:
            continue
        updateProgressBar(file_progress, i)
        files_label.config(text=f"Finished file {i} of {len(filelist)} files.")
        i += 1

    # Print that the process is finished
    details_text.insert(END, "\n.. finished\n")
    details_text.insert(END, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
