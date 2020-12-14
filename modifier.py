# minecraft import
import anvil

# Own imports
import config as cfg
from block_tests import is_solid

class Modifier():
    def __init__(self, identifier):
        self.identifier = identifier

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

    ###############################################################################################

    # self.make_tunnel([500,0,0], [2000,0,1024])
    # self.make_tunnel([0,0,500], [1000,0,2000])
    def make_tunnel(self, start, end):
        # Get region files from global position
        start_x = int(start[0] / cfg.REGION_C_X)
        start_z = int(start[2] / cfg.REGION_C_Z)

        end_x = int(end[0] / cfg.REGION_C_X)
        end_z = int(end[2] / cfg.REGION_C_Z)

        print(start_x, start_z)
        print(end_x, end_z)
        if abs(start_x - end_x) > abs(start_z - end_z):
            window_idxs = [(i, j) for i, j in
                            itertools.product(range(start_x, end_x + 1),
                                              range(start_z, start_z + 1))]

            window_idxs += [(i, j) for i, j in
                            itertools.product(range(end_x, end_x + 1),
                                              range(start_z + 1, end_z + 1))]
        else:
            window_idxs = [(i, j) for i, j in
                            itertools.product(range(start_x, start_x + 1),
                                              range(start_z, end_z + 1))]

            window_idxs += [(i, j) for i, j in
                            itertools.product(range(start_x + 1, end_x + 1),
                                              range(end_z, end_z + 1))]
        print(window_idxs)

        regions = []
        for pos in window_idxs:
            filename = "r." + str(pos[0]) + "." + str(pos[1]) + ".mca"
            regions.append(filename)

        print(regions)
