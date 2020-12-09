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
        self.apocket_size = int(meta_info.apocket_size.get())
        self.repl_area = int(meta_info.repl_area.get()) * 2 + 1

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

        # TODO this is a stupid way to loop since neither the block nor the chunk are used
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
            elif states[x + self.offset_x, y, z + self.offset_z] > 0:
                self.identified[x, y, z] = UNCHANGED
            else:
                self.identified[x, y, z] = UNCHANGED
                print("Error in identifier.")

            # TODO
            if z == 15 and x == 15:
                y += 1
            if x == 15:
                z = (z + 1) % 16
            x = (x + 1) % 16

        return [self.changeCountWater, self.changeCountAir, self.changeCountRepl]

    def identify_label(self, classified_air_region, classified_water_region, classified_repl_region):
        # TODO use a different way to bild this array np.ones((self.repl_area, self.repl_area, self.repl_area))
        str_3D=np.array([[[1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]],

            [[1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]],

            [[1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]]])

        # times
        # classify: 77517
        # identify: 175945
        # modify: 560962
        # save: 180618
        # total: 996793

        # TODO
        from scipy.ndimage import label as label2
        # arr, num = label2(classified_region, str_3D)

        # print(f"label2 num: {num}")

        from skimage.measure import label

        # np.savetxt('data2.csv', arr[1], fmt='%i', delimiter=',')
        # np.savetxt('data.csv', self.classified_region[1], fmt='%i', delimiter=',')
        # arr1, num1 = label(classified_air_region, connectivity=2, return_num=True, background=0)
        arr1, num1 = label2(classified_air_region, str_3D)
        arr2, num2 = label(classified_water_region, connectivity=2, return_num=True, background=0) # TODO g_background

        from scipy import ndimage
        classified_repl_region = ndimage.binary_erosion(classified_repl_region, structure=np.ones((self.repl_area, self.repl_area, self.repl_area))).astype(classified_repl_region.dtype)
        arr3, num3 = label(classified_repl_region, connectivity=2, return_num=True, background=0)
        print(num1)
        print(num2)
        print(num3)

        self.blocks_chunk_x = 16
        self.blocks_chunk_y = 256
        self.blocks_chunk_z = 16
        self.max_chunk_x = 32
        self.max_chunk_z = 32
        self.identified = np.zeros((self.blocks_chunk_x * self.max_chunk_x, self.blocks_chunk_y, self.blocks_chunk_z * self.max_chunk_z), dtype=int)

        changeCountWater = 0
        changeCountAir = 0
        changeCountRepl = 0

        air_p_size = 1
        water_p_size = 1

        # num: 49
        # 1: 49193926
        # 3: 17914938
        # for idx in range(0, 10):
        #     result = np.nonzero(classified_region == idx)
        #     print(f"Length of classified_region == {idx}")
        #     print(len(result[0]))

        # TODO parallelise

        # TODO check for amount num1 after waterfix -> last label count = 503
        for idx in range(1, num1):
            result = np.nonzero(arr1 == idx)
            lenght = len(result[0])

            # TODO use parameter for length
            if lenght <= self.apocket_size and self.check_all(classified_air_region, result, G_AIR):
                self.fill_array(result, AIRPOCKET)
                changeCountAir += lenght

        # last label count = 9

        # TODO the problem is, that the blocks are first replaced with water but
        # afterwards replaced again due to the relacementtest
        # for smaller sizes this should be fixed by the tickness test, but for bigger pockets
        # it is recommended to first do the replace and afterwards do the waterblocks
        for idx in range(1, num2):
            result = np.nonzero(arr2 == idx)
            lenght = len(result[0])

            if lenght <= self.wp_size:
                self.fill_array(result, WATERBLOCK)
                changeCountWater += lenght

        # last label count = 56
        for idx in range(1, num3):
            result = np.nonzero(arr3 == idx)

            # x = result[0][0]
            # y = result[1][0]
            # z = result[2][0]

            #block_class = classified_repl_region[x, y, z]
            lenght = len(result[0])

            # if self.air_pockets == 1 and lenght <= air_p_size and block_class == G_AIR:
            #     self.fill_array(result, AIRPOCKET)
            #     changeCountAir += lenght
            # elif self.water_blocks == 1 and lenght <= water_p_size and block_class == G_SOLID:
            #     # TODO water check is missing
            #     # TODO water could be below and air above
            #     self.fill_array(result, WATERBLOCK)
            #     changeCountWater += lenght
            # # TODO bordercheck needed here
            # if self.repl_blocks == 1 and block_class == G_SOLID: # TODO
            self.fill_array(result, SOLIDAREA)
            changeCountRepl += lenght

            # if idx % 20 == 0:
            #     print(idx)

        # 17914937
        # print(changeCountRepl)

        # for idx in range(4, 5):
        #     result = np.nonzero(self.identified == idx)
        #     print(f"Length of self.identified == {idx}")
        #     print(len(result[0]))

        return [changeCountWater, changeCountAir, changeCountRepl]

        # print(num)
        # np.savetxt('data2.csv', arr[1], fmt='%i', delimiter=',')

    # TODO is there a numpy function for this?
    def fill_array(self, result, value):
        self.identified[result[0], result[1], result[2]] = value

        # list_of_indices = list(zip(result[0], result[1], result[2]))

        # for xyz in list_of_indices:
        #     x2, y2, z2 = xyz
        #     self.identified[x2, y2, z2] = value

    # TODO can this be done better?

    # Returns false if there is a value in the array that is not equal to the value-parameter
    def check_all(self, array, result, value):
        list_of_indices = list(zip(result[0], result[1], result[2]))

        for xyz in list_of_indices:
            x, y, z = xyz
            if array[x, y, z] != value:
                return False
        return True
