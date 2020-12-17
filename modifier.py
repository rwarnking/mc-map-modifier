# minecraft import
import anvil

# Own imports
import config as cfg
from block_tests import is_solid, is_hot

class Modifier():
    def __init__(self, identifier):
        self.identifier = identifier

        self.air = anvil.Block('minecraft', 'air')
        self.stone = anvil.Block('minecraft', 'stone')
        self.glass = anvil.Block('minecraft', 'glass')

        self.torch = anvil.Block('minecraft', 'torch')
        self.r_torch = anvil.Block('minecraft', 'redstone_torch')


    def modify(self, chunk, repl_chunk, new_region, chunk_x, chunk_z):
        new_chunk = 0
        x = 0
        y = 0
        z = 0

        # Create `Block` objects that are used to set blocks
        water = anvil.Block('minecraft', 'water')
        diamond_block = anvil.Block('minecraft', 'diamond_block')
        gold_block = anvil.Block('minecraft', 'gold_block')
        blue_wool = anvil.Block('minecraft', 'blue_wool')

        # Iterate all blocks and select write the new block to the new_chunk
        for block in chunk.stream_chunk():
            b = block

            if b.id == 'chest':
                print(b.properties)

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
                    b = self.stone
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

    # TODO using multi processing for the block assignment to the chunks was tried once
    # using the multiprocessing manager list, this did not lead to acceptable results,
    # since the needed time for 100 elements was already similar to the complete duration
    # of the single process function. The problem may be the big data structure that is build
    # and needs to be serialised for the shared usage. Using a different type of multiprocessing
    # may solve this but was not tried.
    def copy_chunks_mp(self, new_region, region, repl_region):
        # Create pairs to index the different chunks -> (0, 0) (0, 1) (0, m) (1, 0) (2, 0) (n, m)
        # TODO
        import itertools
        import multiprocessing as mp
        from contextlib import closing
        window_idxs = [(i, j) for i, j in
                    itertools.product(range(cfg.REGION_C_X),
                        range(cfg.REGION_C_Z))]

        import multiprocessing
        manager = multiprocessing.Manager()
        chunks = manager.list([None] * 1024)

        with closing(mp.Pool(processes=4, initializer = self.init_worker, initargs = (new_region, region, repl_region, chunks))) as pool:
            res = pool.map(self.worker_task, window_idxs)

        pool.close()
        pool.join()

        new_region.chunks = chunks

    ###############################################################################################

    # self.make_tunnel([500,0,0], [2000,0,1024])
    # self.make_tunnel([0,0,500], [1000,0,2000])
    def make_tunnel(self, region, new_region, rX, rZ, start, end):
        # corner = start[0] != end[0] and start[2] != end[2]

        # Get region files from global position
        start_r_x = int(start[0] / cfg.REGION_B_X)
        start_r_z = int(start[2] / cfg.REGION_B_Z)

        end_r_x = int(end[0] / cfg.REGION_B_X)
        end_r_z = int(end[2] / cfg.REGION_B_Z)

        # print(start_r_x, start_r_z)
        # print(end_r_x, end_r_z)
        # if abs(start_r_x - end_r_x) > abs(start_r_z - end_r_z):
        #     window_idxs = [(i, j) for i, j in
        #                     itertools.product(range(start_r_x, end_r_x + 1),
        #                                       range(start_r_z, start_r_z + 1))]

        #     window_idxs += [(i, j) for i, j in
        #                     itertools.product(range(end_r_x, end_r_x + 1),
        #                                       range(start_r_z + 1, end_r_z + 1))]
        # else:
        #     window_idxs = [(i, j) for i, j in
        #                     itertools.product(range(start_r_x, start_r_x + 1),
        #                                       range(start_r_z, end_r_z + 1))]

        #     window_idxs += [(i, j) for i, j in
        #                     itertools.product(range(start_r_x + 1, end_r_x + 1),
        #                                       range(end_r_z, end_r_z + 1))]
        # print(window_idxs)

        # if [rX, rZ] in window_idxs
        region_min_x = rX * cfg.REGION_B_X
        region_max_x = (rX + 1) * cfg.REGION_B_X
        region_min_z = rZ * cfg.REGION_B_Z
        region_max_z = (rZ + 1) * cfg.REGION_B_Z

        torch_dist = 5
        dir_r_x = end_r_x
        dir_r_z = start_r_z
        if abs(start_r_x - end_r_x) < abs(start_r_z - end_r_z):
            dir_r_x = start_r_x
            dir_r_z = end_r_z

        if dir_r_z == rZ and start_r_x <= rX and end_r_x >= rX:
            this_min_x = start[0] if (start[0] > region_min_x) else region_min_x
            this_max_x = end[0] if (end[0] < region_max_x) else region_max_x
            for x in range(this_min_x, this_max_x):
                self.set_5x5_x(region, new_region, x, start[1], start[2], x % torch_dist == 0)
        if dir_r_x == rX and start_r_z <= rZ and end_r_z >= rZ:
            this_min_z = start[2] if (start[2] > region_min_z) else region_min_z
            this_max_z = end[2] if (end[2] < region_max_z) else region_max_z
            for z in range(this_min_z, this_max_z):
                self.set_5x5_z(region, new_region, start[0], start[1], z, z % torch_dist == 0)


    # TODO these 4 functions should be combinable
    def set_5x5_x(self, region, new_region, x, y, z, place_torch):
        self.set_3x3_x(new_region, x, y, z, place_torch)

        # Top layer
        for add_z in range(-2, 3):
            b = self.get_border_block(region, x, y + 3, z + add_z)
            new_region.set_block(b, x, y + 2, z + add_z)

        # Bottom layer
        for add_z in range(-2, 3):
            b = self.get_border_block(region, x, y - 3, z + add_z)
            new_region.set_block(b, x, y - 2, z + add_z)

        # Left and right
        for add_y in range(-2, 3):
            b = self.get_border_block(region, x, y + add_y, z - 3)
            new_region.set_block(b, x, y + add_y, z - 2)
            b = self.get_border_block(region, x, y + add_y, z + 3)
            new_region.set_block(b, x, y + add_y, z + 2)

        if place_torch and self.test_floor(region, x, y, z):
            for i in range(-1, 2):
                for j in range(0, 2):
                    for k in range(-1, 2):
                        new_region.set_block(self.stone, x + i, y - 3 - j, z + k)
            new_region.set_block(self.r_torch, x, y - 3, z)
        elif place_torch:
            new_region.set_block(self.r_torch, x, y - 1, z + 1)

    def get_border_block(self, region, x, y, z):
        block_r_x = (x % cfg.REGION_B_X)
        block_r_z = (z % cfg.REGION_B_Z)
        chunk = anvil.Chunk.from_region(region, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z))
        block = chunk.get_block(block_r_x % cfg.CHUNK_B_X, y, block_r_z % cfg.CHUNK_B_Z)

        if is_hot(block.id):
            return self.glass
        else:
            return self.stone

    def test_floor(self, region, x, y, z):
        y_now = y - 2
        block_r_x = (x % cfg.REGION_B_X)
        block_r_z = (z % cfg.REGION_B_Z)
        for i in range(-1, 2):
            for k in range(-1, 2):
                chunk = anvil.Chunk.from_region(region, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z))
                block = chunk.get_block(block_r_x % cfg.CHUNK_B_X, y_now, block_r_z % cfg.CHUNK_B_Z)
                if is_hot(block.id):
                    return False
        return True

    def set_3x3_x(self, r, x, y, z, place_torch):
        torch = self.torch if place_torch else self.air
        rail = anvil.Block('minecraft', 'powered_rail') if place_torch else anvil.Block('minecraft', 'rail')
        rail.properties['shape'] = 'east_west'
        if place_torch:
            rail.properties['powered'] = 'true'
        # Middle layer -> air
        r.set_block(self.air, x, y, z)
        r.set_block(self.air, x, y, z - 1)
        r.set_block(self.air, x, y, z + 1)
        # Top layer -> air
        r.set_block(self.air, x, y + 1, z)
        r.set_block(self.air, x, y + 1, z - 1)
        r.set_block(self.air, x, y + 1, z + 1)
        # Bot layer -> air, torches, rails and powered rails
        r.set_block(torch, x, y - 1, z - 1)
        r.set_block(rail, x, y - 1, z)
        r.set_block(torch, x, y - 1, z + 1)

    def set_5x5_z(self, region, new_region, x, y, z, place_torch):
        self.set_3x3_z(new_region, x, y, z, place_torch)

        # Top layer
        for add_x in range(-2, 3):
            b = self.get_border_block(region, x + add_x, y + 3, z)
            new_region.set_block(b, x + add_x, y + 2, z)

        # Bottom layer
        for add_x in range(-2, 3):
            b = self.get_border_block(region, x + add_x, y - 3, z)
            new_region.set_block(b, x + add_x, y - 2, z)

        # Left and right
        for add_y in range(-2, 3):
            b = self.get_border_block(region, x - 3, y + add_y, z)
            new_region.set_block(b, x - 2, y + add_y, z)
            b = self.get_border_block(region, x + 3, y + add_y, z)
            new_region.set_block(b, x + 2, y + add_y, z)

        if place_torch and self.test_floor(region, x, y, z):
            for i in range(-1, 2):
                for j in range(0, 2):
                    for k in range(-1, 2):
                        new_region.set_block(self.stone, x + i, y - 3 - j, z + k)
            new_region.set_block(self.r_torch, x, y - 3, z)
        elif place_torch:
            new_region.set_block(self.r_torch, x + 1, y - 1, z)

    def set_3x3_z(self, r, x, y, z, place_torch):
        torch = self.torch if place_torch else self.air
        rail = anvil.Block('minecraft', 'powered_rail') if place_torch else anvil.Block('minecraft', 'rail')
        if place_torch:
            rail.properties['powered'] = 'true'
        # Middle layer -> air
        r.set_block(self.air, x, y, z)
        r.set_block(self.air, x - 1, y, z)
        r.set_block(self.air, x + 1, y, z)
        # Top layer -> air
        r.set_block(self.air, x, y + 1, z)
        r.set_block(self.air, x - 1, y + 1, z)
        r.set_block(self.air, x + 1, y + 1, z)
        # Bot layer -> air, torches, rails and powered rails
        r.set_block(torch, x - 1, y - 1, z)
        r.set_block(rail, x, y - 1, z)
        r.set_block(torch, x + 1, y - 1, z)
