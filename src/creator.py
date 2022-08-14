import anvil  # minecraft import
import config as cfg  # own import
from anvil.errors import OutOfBoundsCoordinates
from block_tests import is_hot, is_repl_block  # own imports
from nbt import nbt  # minecraft import

from identifier import Identifier
from meta_information import Counts

class Creator:
    def __init__(self, identifier : Identifier):
        self.identifier = identifier

    def create_region(self, regions, counts : Counts, timer):
        # Iterate all chunks of a region, so the complete region can be copied
        # chunk_z before chunk_x, order matters otherwise the chunks
        # are not in the right direction
        for chunk_z in range(cfg.REGION_C_X):

            timer.start_time()
            for chunk_x in range(cfg.REGION_C_Z):
                self.create_chunk(regions, chunk_x, chunk_z)
                counts.chunks_m.value += 1

            timer.end_time()
            timer.update_m_elapsed(counts)

    ###############################################################################################

    def create_chunk(self, regions, chunk_x, chunk_z):
        """
        Creates a chunk with the final data. The identified array is sampled
        for each block and interpreted corresponding to the enabled rules.
        After the chunk was created the chunk is assigned to the new region
        and compressed, so it does not need that much memory.
        """
        old_r = regions["old_r"]
        repl_r = regions["repl_r"]
        new_r = regions["new_r"]

        old_chunk = None
        try:
            old_chunk = anvil.Chunk.from_region(old_r, chunk_x, chunk_z)
        except Exception:
            # TODO
            print(f"skipped non-existent chunk ({chunk_x}, {chunk_z})")

        if old_chunk:
            # TODO only when the option is ticked?
            repl_chunk = False
            if repl_r:
                try:
                    repl_chunk = anvil.Chunk.from_region(repl_r, chunk_x, chunk_z)
                except Exception:
                    print(f"Could not create replacement chunk for {chunk_x}, {chunk_z}.")

            new_chunk = new_r.get_chunk(chunk_x, chunk_z)
            if new_chunk == None:
                new_chunk = anvil.EmptyChunk(chunk_x, chunk_z)

            self.select_chunk_blocks(
                old_chunk,
                repl_chunk,
                new_chunk,
                (new_r.x, new_r.z),
                chunk_x,
                chunk_z,
            )
            # Assign the new_chunk to the region, so it can be compressed.
            # The old_region is needed for additional metadata
            new_r.set_chunk(new_chunk, regions["old_r"])

    def select_chunk_blocks(self, old_chunk, repl_chunk, new_chunk, region_id, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0

        # Create `Block` objects that are used to set blocks
        water = anvil.Block("minecraft", "water")
        diamond_block = anvil.Block("minecraft", "diamond_block")
        # gold_block = anvil.Block("minecraft", "gold_block")
        # blue_wool = anvil.Block("minecraft", "blue_wool")

        b = 0
        xyz = 0
        x_region = 0
        z_region = 0
        x_global = 0
        z_global = 0

        # Iterate all blocks and select write the new block to the new_chunk
        # Even though the block is sometimes overriden it is faster to use
        # the stream_chunk option than using old_chunk.get_block(...)
        for block in old_chunk.stream_chunk():
            b = block

            x_region = chunk_x * cfg.CHUNK_B_X + x
            z_region = chunk_z * cfg.CHUNK_B_Z + z
            x_global = region_id[0] * cfg.REGION_B_X + x_region
            z_global = region_id[1] * cfg.REGION_B_Z + z_region

            xyz = self.identifier.identified[x_region, y, z_region]
            if xyz == cfg.TUNNEL:
                # TODO get block to set block
                b = new_chunk.get_block(x, y, z)
            elif xyz == cfg.WATERBLOCK:
                b = water
                print(f"Found water Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})")
                print(f"GlobalPos: ({x_global}, {y}, {z_global})")
            elif xyz == cfg.AIRPOCKET:
                if repl_chunk:
                    b = self.get_replacement_block(repl_chunk, x, y, z)
                else:
                    b = self.stone
                print(f"Found airpocket Block ({x},{y},{z}) in Chunk ({chunk_x}, {chunk_z})")
                print(f"GlobalPos: ({x_global}, {y}, {z_global})")
            elif xyz == cfg.SOLIDAREA:
                if repl_chunk:
                    b = self.get_replacement_block(repl_chunk, x, y, z)
                # b = self.get_replacement_block(repl_chunk, x, y, z)
                if repl_chunk:
                    new_block = repl_chunk.get_block(x, y, z)
                    # Replace the block if it is solid but use the original when it is not
                    if is_repl_block(new_block.id):
                        b = new_block
                    # TODO debug version
                    b = diamond_block
            elif xyz != cfg.UNCHANGED:
                print(
                    f"Found unidentified Block ({x},{y},{z}) "
                    f"in Chunk ({chunk_x}, {chunk_z}) with {xyz}."
                )
                print(f"GlobalPos: ({x_global}, {y}, {z_global})")

            try:
                new_chunk.set_block(b, x, y, z)
            except OutOfBoundsCoordinates:
                print(f"could not set Block ({x},{y},{z})")

            if x == (cfg.CHUNK_B_X - 1) and z == (cfg.CHUNK_B_Z - 1):
                y += 1
            if x == (cfg.CHUNK_B_X - 1):
                z = (z + 1) % cfg.CHUNK_B_Z
            x = (x + 1) % cfg.CHUNK_B_X

    def get_replacement_block(self, repl_chunk, x, y, z):
        gold_block = anvil.Block("minecraft", "gold_block")

        b = gold_block
        # if repl_chunk:
        #     new_block = repl_chunk.get_block(x, y, z)
        #     # TODO expand is_solid list
        #     if is_solid(new_block.id):
        #         b = new_block
        #         b = blue_wool

        return b
