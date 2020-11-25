# minecraft import
import anvil

# Needed for the file iteration
import os

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
def solidNeighbours(chunk, x, y, z):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            for k in range(z - 1, z + 2):
                if (not (x == i and y == j and z == k)
                    and i >= 0 and j >= 0 and k >= 0
                    and i < 16 and j < 256 and k < 16):
                    block = chunk.get_block(i, j, k)
                    if block.id == 'air':
                        return False
    return True

###################################################################################################
# Copy
###################################################################################################
def copyChunk(newRegion, region, chunkX, chunkZ):
    try:
        chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)

        # newChunk = newRegion.add_chunk(anvil.EmptyChunk(chunkX, chunkZ))
        newChunk = 0

        x = 0
        y = 0
        z = 0

        index = 0
        for block in chunk.stream_chunk():
            b = block
            # print(f'{block.id} - ({x},{y},{z}) - {index}')
            # TODO: compute coordinates from chunk and index
            # TODO this wants global coordinates but gets region coords
            # if block.id == 'air' and solidNeighbours(chunk, x, y, z):
            #     b = dirt
            #     print(f'Changed: {x} {y} {z}')
            #     change_count += 1


            try:
                newChunk = newRegion.set_block(b, newRegion.x * 512 + chunkX * 16 + x, y, newRegion.z * 512 + chunkZ * 16 + z)
            except:
                print(f'could not set Block ({x},{y},{z})')
            index += 1

            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        newChunk.set_data(chunk.data)

        print(f'finished chunk ({chunkX},{chunkZ})')
    except:
        print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

###################################################################################################

def copyRegion(chunk_progress, chunk_label, src_dir, target_dir, filename):
    l = filename.split('.')
    rX = int(l[1])
    rZ = int(l[2])

    # Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
    newRegion = anvil.EmptyRegion(rX, rZ)

    #path = 'original/'
    #filename = 'r.'+str(rX)+'.'+str(rZ)+'.mca'
    print(src_dir + "/" + filename)
    region = anvil.Region.from_file(src_dir + "/" + filename)

    # Create `Block` objects that are used to set blocks
    # stone = anvil.Block('minecraft', 'stone')
    dirt = anvil.Block('minecraft', 'dirt')

    change_count = 0

    max_chunkX = 3
    max_chunkZ = 3
    chunk_progress["maximum"] = max_chunkX * max_chunkZ
    chunk_label.config(text=f"Finished chunk 0, 0 of {max_chunkX - 1}, {max_chunkZ - 1}. And 0 of {max_chunkX * max_chunkZ} chunks.")

    for chunkX in range(max_chunkX):
        for chunkZ in range(max_chunkZ):

            copyChunk(newRegion, region, chunkX, chunkZ)

            updateProgressBar(chunk_progress, chunkZ + 1 + chunkX * max_chunkZ)
            chunk_label.config(text=f"Finished chunk {chunkX}, {chunkZ} of {max_chunkX - 1}, {max_chunkZ - 1}. And {chunkZ + 1 + chunkX * max_chunkZ} of {max_chunkX * max_chunkZ} chunks.")

    print(f'Changed {change_count} blocks')

    # Save to a file
    #path = 'original_copy/'
    #filename = 'r.'+str(rX)+'.'+str(rZ)+'.mca'
    newRegion.save(target_dir + "/" + filename)

###################################################################################################
# Main
###################################################################################################
def run(src_dir,
    chunk_progress, file_progress,
    chunk_label, files_label,
    water_blocks, air_blocks, new_blocks):

    if (water_blocks.get() == 1):
        print("Water Blocks are getting fixed!")
    else:
        print("Water Blocks are not getting fixed!")

    if (air_blocks.get() == 1):
        print("Air Blocks are getting fixed!")
    else:
        print("Air Blocks are not getting fixed!")

    if (new_blocks.get() == 1):
        print("New Blocks are getting fixed!")
    else:
        print("New Blocks are not getting fixed!")

    print('.. starting')
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    filelist = os.listdir(src_dir)
    if len(filelist) == 0:
        print("No files found! Select a different source path.")
        return

    try:
        target_dir = src_dir + "_copy"
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
    except OSError:
        print ("Creation of the directory %s failed" % target_dir)
    else:
        print ("Successfully created the directory %s " % target_dir)

    file_progress["maximum"] = len(filelist)
    files_label.config(text=f"Finished file {0} of {len(filelist)} files.")

    i = 1
    for filename in filelist:
        if filename.endswith(".mca"):
            copyRegion(chunk_progress, chunk_label, src_dir, target_dir, filename)
        else:
            continue
        updateProgressBar(file_progress, i)
        files_label.config(text=f"Finished file {i} of {len(filelist)} files.")
        i += 1

    print('.. finished')
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
