# For array manipulations
import numpy as np

UNCHECKED = 0
UNCHANGED = 1
WATERBLOCK = 2
AIRPOCKET = 3
SOLIDAREA = 4

# TODO have this only once
G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

class Identifier:

    def __init__(self, meta_info, c_all = False):
        self.identified = np.zeros((16, 256, 16), dtype=int)

        self.wp_size = int(meta_info.wpocket_size.get())

        self.water_blocks = meta_info.water_blocks.get()
        self.air_pockets = meta_info.air_pockets.get()
        self.repl_blocks = meta_info.repl_blocks.get()

        self.changeCountWater = 0
        self.changeCountAir = 0
        self.changeCountRepl = 0

        if c_all:
            # TODO vars should be variable (16, 32 ...)
            self.upper_bound_x = 16 * 32
            self.upper_bound_z = 16 * 32
            self.offset_x = 1
        else:
            self.upper_bound_x = 15
            self.upper_bound_z = 15
            self.offset_x = 0
            self.offset_z = 0

    ###############################################################################################
    # Checks
    ###############################################################################################
    def check_neighbours_v(self, states, x, y, z, validator, amount = 1):
        if (x <= 0 or y <= 0 or z <= 0
            or x >= self.upper_bound_x or y >= 255 or z >= self.upper_bound_z):
            return False

        for i in range(x - amount, x + amount + 1):
            for j in range(y - amount, y + amount + 1):
                for k in range(z - amount, z + amount + 1):
                    if not (x == i and y == j and z == k):
                        if validator(states[i, j, k]):
                            return False
        return True

    def check_neighbours_v_2(self, states, x, y, z, validator, limit = 1, amount = 1):
        if (x <= 0 or y <= 0 or z <= 0
            or x >= self.upper_bound_x or y >= 255 or z >= self.upper_bound_z):
            return False

        neighbour = True

        for i in range(x - amount, x + amount + 1):
            for j in range(y - amount, y + amount + 1):
                for k in range(z - amount, z + amount + 1):
                    if not (x == i and y == j and z == k):
                        if validator(states[i, j, k]):
                            if neighbour == True:
                                neighbour = [i, j, k]
                            else:
                                return False

        return neighbour

    def check_water_blocks(self, wp_size, states, x, y, z):
        if states[x, y, z] == G_SOLID:
            if wp_size == 1:
                return self.check_neighbours_v(states, x, y, z, lambda s: s != G_WATER)
            # TODO this is kinda stupid because for every block the 2-case applies, the test is run
            # instead mark all blocks that are processed here
            elif wp_size == 2:
                res = self.check_neighbours_v_2(states, x, y, z, lambda s: s != G_WATER)
                if isinstance(res, bool):
                    return res
                res = self.check_neighbours_v_2(states, res[0], res[1], res[2], lambda s: s != G_WATER)
                return res != False
            else:
                return self.check_neighbours_v(states, x, y, z, lambda s: s != G_WATER)
        return False

    def check_air_pockets(self, states, x, y, z):
        if states[x, y, z] == G_AIR:
            return self.check_neighbours_v(states, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
        return False

    def check_solid_area(self, states, x, y, z):
        # TODO what about water? is it in transparent blocks? + lava
        if states[x, y, z] == G_SOLID:
            return self.check_neighbours_v(states, x, y, z, lambda s: s == G_AIR or s == G_WATER or s == G_TRANSPARENT)
        return False

    ###############################################################################################
    # Identification
    ###############################################################################################
    def identify(self, chunk, states, chunk_x, chunk_z):
        x = 0
        y = 0
        z = 0

        if self.offset_x > 0:
            self.offset_x = 16 * chunk_x
            self.offset_z = 16 * chunk_z

        for block in chunk.stream_chunk():
            if self.water_blocks == 1 and self.check_water_blocks(self.wp_size, states, x + self.offset_x, y, z + self.offset_z):
                self.identified[x, y, z] = WATERBLOCK
                self.changeCountWater += 1
            elif self.air_pockets == 1 and self.check_air_pockets(states, x + self.offset_x, y, z + self.offset_z):
                self.identified[x, y, z] = AIRPOCKET
                self.changeCountAir += 1
            elif self.repl_blocks == 1 and self.check_solid_area(states, x + self.offset_x, y, z + self.offset_z):
                self.identified[x, y, z] = SOLIDAREA
                self.changeCountRepl += 1
            else:
                self.identified[x, y, z] = UNCHANGED

            # TODO
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        return [self.changeCountWater, self.changeCountAir, self.changeCountRepl]
