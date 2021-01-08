import os
import anvil  # minecraft import
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import config as cfg  # own import
# from anvil.errors import OutOfBoundsCoordinates
from block_tests import all_transparent_blocks, solid_blocks


class Creator:
    # def __init__(self, identifier):

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

    def water_block_tests(self, new_region):
        return True

    def repl_block_tests(self, new_region):
        return True

    def set_air_cube(self, region, x, y, z, block, thickness, size):
        l = int(thickness / 2.0)
        r = int(thickness / 2.0)
        if thickness % 2 == 0:
            r = r - 1
        for i in range(-l, r + 1):
            for j in range(-l, r + 1):
                for k in range(-l, r + 1):
                    region.set_block(block, x + i, y + j, z + k)

        l = int(size / 2.0)
        r = int(size / 2.0)
        if size % 2 == 0:
            r = r - 1
        for i in range(-l, r + 1):
            for j in range(-l, r + 1):
                for k in range(-l, r + 1):
                    region.set_block(self.air, x + i, y + j, z + k)

###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    c = Creator()
    c.create_test_map()
