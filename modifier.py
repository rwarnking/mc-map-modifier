# minecraft import
import anvil

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
    import time
    progress['value'] = value
    progress.update()
    time.sleep(1)

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
def copyRegion(progress, chunk_label, rX, rZ):
    # Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
    newRegion = anvil.EmptyRegion(rX, rZ)

    path = 'original/'
    filename = 'r.'+str(rX)+'.'+str(rZ)+'.mca'
    print(path + filename)
    region = anvil.Region.from_file(path + filename)

    # Create `Block` objects that are used to set blocks
    # stone = anvil.Block('minecraft', 'stone')
    dirt = anvil.Block('minecraft', 'dirt')

    change_count = 0

    max_chunkX = 3
    max_chunkZ = 3
    progress["maximum"] = max_chunkX * max_chunkZ

    for chunkX in range(max_chunkX):
        for chunkZ in range(max_chunkZ):

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
                        newChunk = newRegion.set_block(b, chunkX * 16 + x, y, chunkZ * 16 + z)
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

                updateProgressBar(progress, chunkZ + 1 + chunkX * max_chunkZ)
                chunk_label.config(text=f"Finished chunk {chunkX}, {chunkZ} of {max_chunkX - 1}, {max_chunkZ - 1}. And {chunkZ + 1 + chunkX * max_chunkZ} of {max_chunkX * max_chunkZ} chunks.")

            except:
                print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

    print(f'Changed {change_count} blocks')

    # Save to a file
    path = 'original_copy/'
    filename = 'r.'+str(rX)+'.'+str(rZ)+'.mca'
    newRegion.save(path + filename)

###################################################################################################
# Main
###################################################################################################
def run(progress, chunk_label, files_label, water_blocks, air_blocks, new_blocks):

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


    # TODO for each file do stuff
    # TODO use second progress bar
    print('.. starting')
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    copyRegion(progress, chunk_label, 0, 0)
    print('.. finished')
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    files_label.config(text=f"Finished file {1} of {1} files.")

    # max = 11
    # for i in range(max):
    #     updateProgressBar(progress, i * 10)
    #     chunk_label.config(text=f"Finished chunk {i} of {max-1} chunks.")
    #     files_label.config(text=f"Finished file {i} of {max-1} files.")
