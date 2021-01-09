import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import anvil  # minecraft import
import config as cfg  # own import
from anvil.errors import OutOfBoundsCoordinates  # TODO
from block_tests import all_transparent_blocks, solid_blocks


class Creator:
    def create_test_map(self, filename="r1.0.0.mca"):
        print("running ...")
        target_dir = os.path.dirname(os.path.abspath(__file__)) + "/region_files_original"
        end = filename.split(".")
        r_x = int(end[1])
        r_z = int(end[2])

        # Create a new region with the `EmptyRegion` class at region coords
        new_region = anvil.EmptyRegion(r_x, r_z)

        self.air_block_tests(new_region)
        self.water_block_tests(new_region)
        self.repl_block_tests(new_region)

        new_region.save(target_dir + "/" + filename)
        print("... finished")

    def air_block_tests(self, new_region):
        self.air = anvil.Block("minecraft", "air")

        max_half_thickness = 4
        g_x = max_half_thickness
        g_y = max_half_thickness
        g_z = max_half_thickness
        for thickness in range(3, 7):
            for size in range(1, thickness - 1):
                for ID in solid_blocks + all_transparent_blocks:
                    if g_z > cfg.REGION_B_Z - max_half_thickness - thickness - 1:
                        print("To many blocks")
                        break

                    b = anvil.Block("minecraft", ID)
                    self.set_air_cube(new_region, g_x, g_y, g_z, b, thickness, size)

                    if g_x < cfg.REGION_B_X - max_half_thickness - thickness - 1:
                        g_x = g_x + thickness + 1
                    elif g_z < cfg.REGION_B_Z - max_half_thickness - thickness - 1:
                        g_x = max_half_thickness
                        g_z = g_z + thickness + 1

                g_x = max_half_thickness
                g_z = g_z + thickness + 1
            g_x = max_half_thickness
            g_z = g_z + thickness + 1

    def get_shape(self, num_blocks):
        shapes = [
            [[[[1]]]],
            [
                [[[1, 1], [0, 0]], [[0, 0], [0, 0]],],
                [[[0, 0], [1, 1]], [[0, 0], [0, 0]],],
                [[[1, 0], [1, 0]], [[0, 0], [0, 0]],],
                [[[0, 1], [0, 1]], [[0, 0], [0, 0]],],
                [[[1, 0], [0, 1]], [[0, 0], [0, 0]],],
                [[[0, 1], [1, 0]], [[0, 0], [0, 0]],],

                [[[0, 0], [0, 0]], [[1, 1], [0, 0]],],
                [[[0, 0], [0, 0]], [[0, 0], [1, 1]],],
                [[[0, 0], [0, 0]], [[1, 0], [1, 0]],],
                [[[0, 0], [0, 0]], [[0, 1], [0, 1]],],
                [[[0, 0], [0, 0]], [[1, 0], [0, 1]],],
                [[[0, 0], [0, 0]], [[0, 1], [1, 0]],],

                [[[0, 1], [0, 0]], [[1, 0], [0, 0]],],
                [[[1, 0], [0, 0]], [[0, 1], [0, 0]],],
                [[[0, 0], [0, 1]], [[0, 0], [1, 0]],],
                [[[0, 0], [1, 0]], [[0, 0], [0, 1]],],
                [[[1, 0], [0, 0]], [[0, 0], [0, 1]],],
                [[[0, 1], [0, 0]], [[0, 0], [1, 0]],],
                [[[0, 0], [0, 1]], [[1, 0], [0, 0]],],
                [[[0, 0], [1, 0]], [[0, 1], [0, 0]],],
            ],
            [
                [
                    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                    [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                ],
            ],
        ]
        return shapes[num_blocks - 1]

    def water_block_tests(self, new_region):
        self.water = anvil.Block("minecraft", "water")
        self.glass = anvil.Block("minecraft", "glass")
        self.stone = anvil.Block("minecraft", "stone")

        thickness = 8
        max_half_thickness = int(thickness / 2)
        g_x = max_half_thickness
        g_y = max_half_thickness + 10
        g_z = max_half_thickness

        for num_blocks in range(1, 4):
            for shape in self.get_shape(num_blocks):
                for ID in solid_blocks + all_transparent_blocks:
                    if g_y > cfg.REGION_B_Y - max_half_thickness - thickness - 1:
                        print("To many blocks")
                        break

                    b = anvil.Block("minecraft", ID)
                    self.set_water_cube(new_region, g_x, g_y, g_z, b, num_blocks, shape)

                    if g_x < cfg.REGION_B_X - max_half_thickness - thickness - 1:
                        g_x = g_x + thickness + 1
                    elif g_z < cfg.REGION_B_Z - max_half_thickness - thickness - 1:
                        g_x = max_half_thickness
                        g_z = g_z + thickness + 1

                g_x = max_half_thickness
                g_z = g_z + thickness + 1
                if g_z > cfg.REGION_B_Z - max_half_thickness - thickness - 1:
                    g_x = max_half_thickness
                    g_y = g_y + thickness + 1
                    g_z = max_half_thickness
            g_x = max_half_thickness
            g_y = g_y + thickness + 1
            g_z = max_half_thickness

    def repl_block_tests(self, new_region):
        return True

    def set_air_cube(self, region, x, y, z, block, thickness, size):
        l = int(thickness / 2.0)
        r = l
        if thickness % 2 == 0:
            r = r - 1
        for i in range(-l, r + 1):
            for j in range(-l, r + 1):
                for k in range(-l, r + 1):
                    region.set_block(block, x + i, y + j, z + k)

        l = int(size / 2.0)
        r = l
        if size % 2 == 0:
            r = r - 1
        for i in range(-l, r + 1):
            for j in range(-l, r + 1):
                for k in range(-l, r + 1):
                    region.set_block(self.air, x + i, y + j, z + k)

    def set_water_cube(self, region, x, y, z, block, num_blocks, shape):
        l2 = int(num_blocks / 2.0)
        r2 = l2
        l = int(num_blocks / 2.0) + 2
        r = l

        if num_blocks % 2 == 0:
            r = r - 1
            r2 = r2 - 1

        for i in range(-l, r + 1):
            for k in range(-l, r + 1):
                region.set_block(self.stone, x + i, y - l, z + k)
                region.set_block(self.stone, x + i, y - l - 1, z + k)

        for j in range(-l + 1, r):
            for i in range(-l, r + 1):
                region.set_block(self.glass, x + i, y + j, z - l)
                region.set_block(self.glass, x + i, y + j, z + r)

            for k in range(-l, r + 1):
                region.set_block(self.glass, x - l, y + j, z + k)
                region.set_block(self.glass, x + r, y + j, z + k)

        for i in range(-l2 - 1, r2 + 2):
            for j in range(-l2 - 1, r2 + 2):
                for k in range(-l2 - 1, r2 + 2):
                    region.set_block(self.water, x + i, y + j, z + k)

        # TODO this should be the same value as num_blocks
        size = len(shape)
        # print(size)
        # print(shape)
        # print(shape[0])
        # print(shape[0][0])
        # print(shape[0][0][0])
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if shape[i][j][k] == 1:
                        region.set_block(block, x + i - l2, y + j - l2, z + k - l2)

###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    c = Creator()
    c.create_test_map()
