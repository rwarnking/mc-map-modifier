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

def copyRegion(rX, rZ):
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

    for chunkX in range(32):
        for chunkZ in range(32):

            try:
                chunk = anvil.Chunk.from_region(region, chunkX, chunkZ)
                # newChunk = newRegion.add_chunk(anvil.EmptyChunk(chunkX, chunkZ))
                newChunk = 0

                x = 0
                y = 0
                z = 0

                index = 0
                for block in chunk.stream_chunk():
                    b = 0
                    # print(f'{block.id} - ({x},{y},{z}) - {index}')
                    # TODO: compute coordinates from chunk and index
                    # TODO this wants global coordinates but gets region coords
                    if block.id == 'air' and solidNeighbours(chunk, x, y, z):
                        #region.set_block(choice((stone, dirt)), x, y, z)
                        b = dirt
                        print(f'Changed: {x} {y} {z}')
                        change_count += 1
                    else:
                        b = block
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
            except:

                # air = anvil.Block('minecraft', 'air')

                # for y in range(256):
                #     for z in range(16):
                #         for x in range(16):
                #             newRegion.set_block(air, x, y, z)

                print(f'skipped non-existent chunk ({chunkX},{chunkZ})')

    print(f'Changed {change_count} blocks')

    # Save to a file
    path = 'original_copy/'
    filename = 'r.'+str(rX)+'.'+str(rZ)+'.mca'
    newRegion.save(path + filename)

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


print('.. starting')
print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
# copyRegion(0, 0)
# printRegion('r.0.0.mca')
print('.. finished')
print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
