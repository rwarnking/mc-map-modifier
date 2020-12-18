# minecraft import
import anvil
from nbt import nbt

# Own imports
import config as cfg
from block_tests import is_solid, is_hot, is_repl_block

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

        region_min_x = rX * cfg.REGION_B_X
        region_max_x = (rX + 1) * cfg.REGION_B_X
        region_min_z = rZ * cfg.REGION_B_Z
        region_max_z = (rZ + 1) * cfg.REGION_B_Z

        self.item_dict = {}

        torch_dist = 5
        dir_r_x = start_r_x
        dir_r_z = end_r_z
        new_x = end[0]
        new_z = start[2]
        direction = cfg.M_DIR_X
        # TODO this does not really work for negative numbers
        if abs(end[0] - start[0]) < abs(end[2] - start[2]):
            dir_r_x = end_r_x
            dir_r_z = start_r_z
            new_x = start[0]
            new_z = end[2]
            direction = cfg.M_DIR_Z

        # TODO height is not dynamic (start[1])
        if dir_r_z == rZ and start_r_x <= rX and end_r_x >= rX:
            this_min_x = start[0] if (start[0] > region_min_x) else region_min_x
            this_max_x = end[0] if (end[0] < region_max_x) else region_max_x
            for x in range(this_min_x, this_max_x):
                self.set_5x5_x(region, new_region, x, start[1], new_z, x % torch_dist == 0)
        if dir_r_x == rX and start_r_z <= rZ and end_r_z >= rZ:
            this_min_z = start[2] if (start[2] > region_min_z) else region_min_z
            this_max_z = end[2] if (end[2] < region_max_z) else region_max_z
            for z in range(this_min_z, this_max_z):
                self.set_5x5_z(region, new_region, new_x, start[1], z, z % torch_dist == 0)

        # TODO gui
        if True:
            self.place_chests(new_region, start[0], start[1], start[2], direction)


    # TODO these 2 functions should be combinable
    def set_5x5_x(self, region, new_region, x, y, z, place_torch):
        self.set_3x3(new_region, x, y, z, place_torch)
        self.get_blocks_3x3(region, x, y, z)

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

        if place_torch:
            self.place_r_torch(region, new_region, x, y, z)

    def set_5x5_z(self, region, new_region, x, y, z, place_torch):
        self.set_3x3(new_region, x, y, z, place_torch, cfg.M_DIR_Z)
        self.get_blocks_3x3(region, x, y, z)

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

        if place_torch:
            self.place_r_torch(region, new_region, x, y, z)

    def place_r_torch(self, region, new_region, x, y, z):
        if self.test_floor(region, x, y, z):
            for i in range(-1, 2):
                for j in range(0, 2):
                    for k in range(-1, 2):
                        new_region.set_block(self.stone, x + i, y - 3 - j, z + k)
            new_region.set_block(self.r_torch, x, y - 3, z)
        else:
            new_region.set_block(self.r_torch, x + 1, y - 1, z)

    def set_3x3(self, r, x, y, z, place_torch, direction = cfg.M_DIR_X):
        torch = self.torch if place_torch else self.air
        rail = anvil.Block('minecraft', 'powered_rail') if place_torch else anvil.Block('minecraft', 'rail')
        if place_torch:
            rail.properties['powered'] = 'true'

        x_m_one = x - 1
        x_p_one = x + 1
        z_m_one = z
        z_p_one = z
        if direction == cfg.M_DIR_X:
            rail.properties['shape'] = 'east_west'
            x_m_one = x
            x_p_one = x
            z_m_one = z - 1
            z_p_one = z + 1

        # Middle layer -> air
        r.set_block(self.air, x, y, z)
        r.set_block(self.air, x_m_one, y, z_m_one)
        r.set_block(self.air, x_p_one, y, z_p_one)
        # Top layer -> air
        r.set_block(self.air, x, y + 1, z)
        r.set_block(self.air, x_m_one, y + 1, z_m_one)
        r.set_block(self.air, x_p_one, y + 1, z_p_one)
        # Bot layer -> air, torches, rails and powered rails
        r.set_block(torch, x_m_one, y - 1, z_m_one)
        r.set_block(rail, x, y - 1, z)
        r.set_block(torch, x_p_one, y - 1, z_p_one)

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

    def get_blocks_3x3(self, region, x, y, z):
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    block_r_x = ((x + i) % cfg.REGION_B_X)
                    block_r_z = ((z + k) % cfg.REGION_B_Z)
                    chunk = anvil.Chunk.from_region(region, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z))
                    block = chunk.get_block(block_r_x % cfg.CHUNK_B_X, y + j, block_r_z % cfg.CHUNK_B_Z)

                    if is_repl_block(block.id):
                        if block.id in self.item_dict:
                            self.item_dict[block.id] += 1
                        else:
                            self.item_dict[block.id] = 1

    def place_chests(self, new_region, x, y, z, direction):
        add_x = 1
        add_z = 0
        chest = anvil.Block('minecraft', 'chest')
        chest.properties['waterlogged'] = 'false'
        chest.properties['facing'] = 'east'
        chest.properties['type'] = 'single'

        if direction == cfg.M_DIR_Z:
            add_x = 0
            add_z = 1
            #chest.properties['shape'] = 'east_west'

        i = 0
        chest_x = x
        chest_y = y - 1
        chest_z = z

        for item_type in self.item_dict:
            amount = self.item_dict[item_type]

            while amount > 0:
                if direction == cfg.M_DIR_Z:
                    chest_x = x + 1
                    chest_z = z + i
                else:
                    chest_x = x + i
                    chest_z = z + 1

                new_region.set_block(chest, chest_x, chest_y, chest_z)

                item = 'minecraft:' + str(item_type)
                block_entity, amount = self.create_chest_block_entity(chest_x, chest_y, chest_z, item, amount)

                chunk_idx_x = chest_x // cfg.CHUNK_B_X
                chunk_idx_z = chest_z // cfg.CHUNK_B_Z
                chunk = new_region.get_chunk(chunk_idx_x, chunk_idx_z)

                if chunk.data['TileEntities'].tagID != nbt.TAG_Compound.id:
                    chunk.data['TileEntities'] = nbt.TAG_List(name='TileEntities', type=nbt.TAG_Compound)
                chunk.data['TileEntities'].tags.append(block_entity)
                i += 1

    def create_chest_block_entity(self, chest_x, chest_y, chest_z, b_type, amount):
        items = nbt.TAG_List(name='Items', type=nbt.TAG_Compound)

        # TODO make this variable by using the config file
        stacks = min(amount // 64, 27)
        remainder = amount % 64 if stacks < 27 else 0

        for i in range(stacks):
            chest_entry = nbt.TAG_Compound()
            chest_entry.tags.extend([
                nbt.TAG_Byte(name='Count', value=64),
                nbt.TAG_Byte(name='Slot', value=i),
                nbt.TAG_String(name='id', value=b_type)
            ])
            items.tags.append(chest_entry)

        if stacks < 27:
            chest_entry = nbt.TAG_Compound()
            chest_entry.tags.extend([
                nbt.TAG_Byte(name='Count', value=amount % 64),
                nbt.TAG_Byte(name='Slot', value=stacks),
                nbt.TAG_String(name='id', value=b_type)
            ])
            items.tags.append(chest_entry)

        block_entity = nbt.TAG_Compound()
        block_entity.tags.extend([
            nbt.TAG_String(name='id', value='minecraft:chest'),
            nbt.TAG_Int(name='x', value=chest_x),
            nbt.TAG_Int(name='y', value=chest_y),
            nbt.TAG_Int(name='z', value=chest_z),
            nbt.TAG_Byte(name='keepPacked', value=0)
        ])
        block_entity.tags.append(items)

        new_amount = amount - (stacks * 64 + remainder)
        return block_entity, new_amount
