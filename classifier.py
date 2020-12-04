# minecraft import
import anvil

# For array manipulations
import numpy as np

# Own imports
from block_tests import get_type

class Classifier:

    def __init__(self, all = False):
        self.blocks_chunk_x = 16
        self.blocks_chunk_y = 256
        self.blocks_chunk_z = 16
        self.max_chunk_x = 32
        self.max_chunk_z = 32

        self.all = all
        if self.all:
            self.classified_region = np.zeros((self.blocks_chunk_x * self.max_chunk_x, self.blocks_chunk_y, self.blocks_chunk_z * self.max_chunk_z), dtype=int)
        else:
            self.classified_region = np.zeros((self.blocks_chunk_x, self.blocks_chunk_y, self.blocks_chunk_z), dtype=int)

    def classify_one(self, chunk, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0
        if self.all:
            c_offset_x = self.blocks_chunk_x * chunk_x
            c_offset_z = self.blocks_chunk_z * chunk_z
        else:
            c_offset_x = 0
            c_offset_z = 0

        for block in chunk.stream_chunk():
            self.classified_region[x + c_offset_x, y, z + c_offset_z] = get_type(block.id)

            # TODO self.blocks_chunk_x
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

    def classify_all(self, region):
        # TODO
        if not self.all:
            print("Error in classifier.")

        chunk = None
        # for chunkX in range(max_chunkX):
        for chunk_x in range(10, 12):
            # for chunkZ in range(max_chunkZ):
            for chunk_z in range(11, 16):

                try:
                    chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                except:
                    print(f'skipped non-existent chunk ({chunk_x}, {chunk_z})')

                if chunk:
                    self.classify_one(chunk, chunk_x, chunk_z)
