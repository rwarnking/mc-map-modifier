import anvil  # minecraft import
import config as cfg  # own import
from anvil.errors import OutOfBoundsCoordinates
from block_tests import is_hot, is_repl_block  # own imports
from nbt import nbt  # minecraft import

from identifier import Identifier
from meta_information import MetaInformation

class Modifier:
    def __init__(self, meta_info : MetaInformation, identifier : Identifier):
        self.identifier = identifier
        self.add_tunnel = meta_info.add_tunnel.get()

        self.tunnel_start = meta_info.get_tunnel_start()
        self.tunnel_end = meta_info.get_tunnel_end()

        self.air = anvil.Block("minecraft", "air")
        self.stone = anvil.Block("minecraft", "stone")
        self.glass = anvil.Block("minecraft", "glass")

        self.torch = anvil.Block("minecraft", "torch")
        self.r_torch = anvil.Block("minecraft", "redstone_torch")
        self.rail = anvil.Block("minecraft", "rail")
        self.powered_rail = anvil.Block("minecraft", "powered_rail")

    def modify(self, regions):
        if self.add_tunnel == 1:
            self.make_tunnel(regions, self.tunnel_start, self.tunnel_end)

    ###############################################################################################
    # Tunnel functions
    ###############################################################################################
    # self.make_tunnel([500,0,0], [2000,0,1024])
    # self.make_tunnel([0,0,500], [1000,0,2000])
    def make_tunnel(self, regions, start, end):
        """
        Adds a tunnel to the new region in regions (new_r) starting at
        the start coordinates leading to the end coordinates.
        When processing the coordinates, they are clamped such that only
        the positions inside the current region are used preventing out of bounds.
        """
        old_r = regions["old_r"]
        new_r = regions["new_r"]
        rX = new_r.x
        rZ = new_r.z

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
        # Clamp the x and z coordinates to match this region
        if dir_r_z == rZ and start_r_x <= rX and end_r_x >= rX:
            this_min_x = start[0] if (start[0] > region_min_x) else region_min_x
            this_max_x = end[0] if (end[0] < region_max_x) else region_max_x
            for x in range(this_min_x, this_max_x):
                self.set_5x5_x(old_r, new_r, x, start[1], new_z, x % torch_dist == 0)
        if dir_r_x == rX and start_r_z <= rZ and end_r_z >= rZ:
            this_min_z = start[2] if (start[2] > region_min_z) else region_min_z
            this_max_z = end[2] if (end[2] < region_max_z) else region_max_z
            for z in range(this_min_z, this_max_z):
                self.set_5x5_z(old_r, new_r, new_x, start[1], z, z % torch_dist == 0)

        # corner = start[0] != end[0] and start[2] != end[2]
        # self.fix_corner(new_region, start, end)

        # TODO gui
        if True:
            self.place_chests(old_r, new_r, start[0], start[1], start[2], direction)

    # TODO these 2 functions should be combinable
    def set_5x5_x(self, old_r, new_r, x, y, z, place_torch):
        self.set_3x3(new_r, x, y, z, place_torch)
        self.get_blocks_3x3(old_r, x, y, z)

        # Top layer
        for add_z in range(-2, 3):
            b = self.get_border_block(old_r, x, y + 3, z + add_z)
            new_r.set_block(b, x, y + 2, z + add_z)
            self.identifier.identified[x, y + 2, z + add_z] = cfg.TUNNEL

        # Bottom layer
        for add_z in range(-2, 3):
            b = self.get_border_block(old_r, x, y - 3, z + add_z)
            new_r.set_block(b, x, y - 2, z + add_z)
            self.identifier.identified[x, y - 2, z + add_z] = cfg.TUNNEL

        # Left and right
        for add_y in range(-2, 3):
            b = self.get_border_block(old_r, x, y + add_y, z - 3)
            new_r.set_block(b, x, y + add_y, z - 2)
            self.identifier.identified[x, y + add_y, z - 2] = cfg.TUNNEL
            b = self.get_border_block(old_r, x, y + add_y, z + 3)
            new_r.set_block(b, x, y + add_y, z + 2)
            self.identifier.identified[x, y + add_y, z + 2] = cfg.TUNNEL

        if place_torch:
            self.place_r_torch(old_r, new_r, x, y, z)

    def set_5x5_z(self, old_r, new_r, x, y, z, place_torch):
        self.set_3x3(new_r, x, y, z, place_torch, cfg.M_DIR_Z)
        self.get_blocks_3x3(old_r, x, y, z)

        # Top layer
        for add_x in range(-2, 3):
            b = self.get_border_block(old_r, x + add_x, y + 3, z)
            new_r.set_block(b, x + add_x, y + 2, z)
            self.identifier.identified[x + add_x, y + 2, z] = cfg.TUNNEL

        # Bottom layer
        for add_x in range(-2, 3):
            b = self.get_border_block(old_r, x + add_x, y - 3, z)
            new_r.set_block(b, x + add_x, y - 2, z)
            self.identifier.identified[x + add_x, y - 2, z] = cfg.TUNNEL

        # Left and right
        for add_y in range(-2, 3):
            b = self.get_border_block(old_r, x - 3, y + add_y, z)
            new_r.set_block(b, x - 2, y + add_y, z)
            self.identifier.identified[x - 2, y + add_y, z] = cfg.TUNNEL
            b = self.get_border_block(old_r, x + 3, y + add_y, z)
            new_r.set_block(b, x + 2, y + add_y, z)
            self.identifier.identified[x + 2, y + add_y, z] = cfg.TUNNEL

        if place_torch:
            self.place_r_torch(old_r, new_r, x, y, z)

    def place_r_torch(self, old_r, new_region, x, y, z):
        if self.test_floor(old_r, x, y, z):
            for i in range(-1, 2):
                for j in range(0, 2):
                    for k in range(-1, 2):
                        new_region.set_block(self.stone, x + i, y - 3 - j, z + k)
            new_region.set_block(self.r_torch, x, y - 3, z)
            self.identifier.identified[x, y - 3, z] = cfg.TUNNEL
        else:
            new_region.set_block(self.r_torch, x + 1, y - 1, z)
            self.identifier.identified[x + 1, y - 1, z] = cfg.TUNNEL

    def set_3x3(self, new_r, x, y, z, place_torch, direction=cfg.M_DIR_X):
        torch = self.torch if place_torch else self.air
        rail = self.powered_rail if place_torch else self.rail
        if place_torch:
            rail.properties["powered"] = "true"

        x_m_one = x - 1
        x_p_one = x + 1
        z_m_one = z
        z_p_one = z
        if direction == cfg.M_DIR_X:
            rail.properties["shape"] = "east_west"
            x_m_one = x
            x_p_one = x
            z_m_one = z - 1
            z_p_one = z + 1

        # Middle layer -> air
        new_r.set_block(self.air, x, y, z)
        new_r.set_block(self.air, x_m_one, y, z_m_one)
        new_r.set_block(self.air, x_p_one, y, z_p_one)
        self.identifier.identified[x, y, z] = cfg.TUNNEL
        self.identifier.identified[x_m_one, y, z_m_one] = cfg.TUNNEL
        self.identifier.identified[x_p_one, y, z_p_one] = cfg.TUNNEL
        # Top layer -> air
        new_r.set_block(self.air, x, y + 1, z)
        new_r.set_block(self.air, x_m_one, y + 1, z_m_one)
        new_r.set_block(self.air, x_p_one, y + 1, z_p_one)
        self.identifier.identified[x, y + 1, z] = cfg.TUNNEL
        self.identifier.identified[x_m_one, y + 1, z_m_one] = cfg.TUNNEL
        self.identifier.identified[x_p_one, y + 1, z_p_one] = cfg.TUNNEL
        # Bot layer -> air, torches, rails and powered rails
        new_r.set_block(torch, x_m_one, y - 1, z_m_one)
        new_r.set_block(rail, x, y - 1, z)
        new_r.set_block(torch, x_p_one, y - 1, z_p_one)
        self.identifier.identified[x_m_one, y - 1, z_m_one] = cfg.TUNNEL
        self.identifier.identified[x, y - 1, z] = cfg.TUNNEL
        self.identifier.identified[x_p_one, y - 1, z_p_one] = cfg.TUNNEL

    def get_border_block(self, old_r, x, y, z):
        block_r_x = x % cfg.REGION_B_X
        block_r_z = z % cfg.REGION_B_Z
        chunk = anvil.Chunk.from_region(
            old_r, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z)
        )
        block = chunk.get_block(block_r_x % cfg.CHUNK_B_X, y, block_r_z % cfg.CHUNK_B_Z)

        if is_hot(block.id):
            return self.glass
        else:
            return self.stone

    def test_floor(self, old_r, x, y, z):
        y_n = y - 2
        block_r_x = x % cfg.REGION_B_X
        block_r_z = z % cfg.REGION_B_Z
        for i in range(-1, 2):
            for k in range(-1, 2):
                chunk = anvil.Chunk.from_region(
                    old_r, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z)
                )
                block = chunk.get_block(block_r_x % cfg.CHUNK_B_X, y_n, block_r_z % cfg.CHUNK_B_Z)
                if is_hot(block.id):
                    return False
        return True

    # def fix_corner(self, new_region, start, end):
    #     if start[0] == end[0] or start[2] == end[2]:
    #         return

    #     corner_pos = [end[0], start[1], start[2]]
    #     if abs(end[0] - start[0]) < abs(end[2] - start[2]):
    #         corner_pos = [start[0], start[1], end[2]]

    def get_blocks_3x3(self, old_r, x, y, z):
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    block_r_x = (x + i) % cfg.REGION_B_X
                    block_r_z = (z + k) % cfg.REGION_B_Z
                    chunk = anvil.Chunk.from_region(
                        old_r, int(block_r_x / cfg.CHUNK_B_X), int(block_r_z / cfg.CHUNK_B_Z)
                    )
                    block = chunk.get_block(
                        block_r_x % cfg.CHUNK_B_X, y + j, block_r_z % cfg.CHUNK_B_Z
                    )

                    if is_repl_block(block.id):
                        if block.id in self.item_dict:
                            self.item_dict[block.id] += 1
                        else:
                            self.item_dict[block.id] = 1

    def place_chests(self, old_r, new_r, x, y, z, direction):
        # add_x = 1
        # add_z = 0
        chest = anvil.Block("minecraft", "chest")
        chest.properties["waterlogged"] = "false"
        chest.properties["facing"] = "east"
        chest.properties["type"] = "single"

        # if direction == cfg.M_DIR_Z:
        #     add_x = 0
        #     add_z = 1
        #     chest.properties["shape"] = "east_west"

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

                new_r.set_block(chest, chest_x, chest_y, chest_z)
                self.identifier.identified[chest_x, chest_y, chest_z] = cfg.TUNNEL

                item = "minecraft:" + str(item_type)
                block_entity, amount = self.create_chest_block_entity(
                    chest_x, chest_y, chest_z, item, amount
                )

                chunk_idx_x = chest_x // cfg.CHUNK_B_X
                chunk_idx_z = chest_z // cfg.CHUNK_B_Z
                chunk = old_r.get_chunk(chunk_idx_x, chunk_idx_z)

                if chunk.data["TileEntities"].tagID != nbt.TAG_Compound.id:
                    chunk.data["TileEntities"] = nbt.TAG_List(
                        name="TileEntities", type=nbt.TAG_Compound
                    )
                chunk.data["TileEntities"].tags.append(block_entity)
                i += 1

    def create_chest_block_entity(self, chest_x, chest_y, chest_z, b_type, amount):
        items = nbt.TAG_List(name="Items", type=nbt.TAG_Compound)

        # TODO make this variable by using the config file
        stacks = min(amount // 64, 27)
        remainder = amount % 64 if stacks < 27 else 0

        for i in range(stacks):
            chest_entry = nbt.TAG_Compound()
            chest_entry.tags.extend(
                [
                    nbt.TAG_Byte(name="Count", value=64),
                    nbt.TAG_Byte(name="Slot", value=i),
                    nbt.TAG_String(name="id", value=b_type),
                ]
            )
            items.tags.append(chest_entry)

        if stacks < 27:
            chest_entry = nbt.TAG_Compound()
            chest_entry.tags.extend(
                [
                    nbt.TAG_Byte(name="Count", value=amount % 64),
                    nbt.TAG_Byte(name="Slot", value=stacks),
                    nbt.TAG_String(name="id", value=b_type),
                ]
            )
            items.tags.append(chest_entry)

        block_entity = nbt.TAG_Compound()
        block_entity.tags.extend(
            [
                nbt.TAG_String(name="id", value="minecraft:chest"),
                nbt.TAG_Int(name="x", value=chest_x),
                nbt.TAG_Int(name="y", value=chest_y),
                nbt.TAG_Int(name="z", value=chest_z),
                nbt.TAG_Byte(name="keepPacked", value=0),
            ]
        )
        block_entity.tags.append(items)

        new_amount = amount - (stacks * 64 + remainder)
        return block_entity, new_amount
