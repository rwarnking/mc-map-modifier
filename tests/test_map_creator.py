import os
import sys
import math

import anvil  # minecraft import

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import config as cfg  # own import
from block_tests import all_transparent_blocks, solid_blocks
from shape_generator import ShapeGenerator


class Vector:
    def __init__(self, x: int=0, y: int=0, z:int=0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_one_val(cls, val: int):
        return cls(val, val, val)

    @classmethod
    def from_array(cls, xyz: [int]):
        return cls(x[0], y[1], z[2])

    def add_vec(self, vec: "Vector"):
        self.x += vec.x
        self.y += vec.y
        self.z += vec.z


class BlockPosition:
    def __init__(self, min_w: int, max_w: int, x: int=None, y: int=None, z:int=None):
        self.dist = 1
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()

        if x is None or y is None or z is None:
            self.xyz = Vector.from_one_val(self.half_width)
        else:
            self.xyz = Vector(x, y, z)

    @classmethod
    def from_one_coord(cls, width: int, val: int):
        return cls(width, val, val, val)

    def reset_no_y(self, min_w: int, max_w: int):
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()
        self.xyz = Vector(self.half_width, self.xyz.y, self.half_width)
        self.next_y()

    def increase_width(self, amount: int=1):
        self.decrease_width(amount)

    def decrease_width(self, amount: int=-1):
        self.now_width += amount
        self.update_width()

    def update_width(self):
        self.half_width = math.ceil((self.now_width + 1) / 2)
        self.limit = Vector(
            cfg.REGION_B_X - self.now_width - self.half_width - self.dist,
            cfg.REGION_B_Y - self.now_width - self.half_width - self.dist,
            cfg.REGION_B_Z - self.now_width - self.half_width - self.dist
        )

    def next_pos(self):
        if self.xyz.x < self.limit.x:
            self.next_x()
        elif self.xyz.z < self.limit.z:
            self.next_z()
        elif self.xyz.y < self.limit.y:
            self.next_y()
        else:
            raise Exception("No positions left!")

    def next_x(self):
        self.xyz.x += self.now_width + self.dist

    def next_y(self, add: bool=False):
        self.xyz.x = self.half_width
        self.xyz.y += self.now_width + self.dist
        self.xyz.z = self.half_width

        if add and self.now_width % 2 == 0:
            self.xyz.y += 1
        if self.xyz.y > self.limit.y:
            raise Exception("Y border value reached!")

    def next_z(self):
        self.xyz.x = self.half_width
        self.xyz.z += self.now_width + self.dist


class TestMapCreator:
    def __init__(self):
        self.shape_generator = ShapeGenerator()
        min_cube_width = 3
        max_cube_width = 7
        self.pos = BlockPosition(min_cube_width, max_cube_width)

    def create_test_map(self, filename: str="r1.0.0.mca"):
        print("running ...")
        target_dir = os.path.dirname(os.path.abspath(__file__)) + "/region_files_original"
        end = filename.split(".")
        r_x = int(end[1])
        r_z = int(end[2])

        # Create a new region with the `EmptyRegion` class at region coords
        new_region = anvil.EmptyRegion(r_x, r_z)

        print("... starting airblock tests ...")
        self.air_block_tests(new_region)
        print("... starting waterblock tests ...")
        self.pos.reset_no_y(5, 7)
        self.water_block_tests(new_region)
        print("... starting replblock tests ...")
        self.pos.reset_no_y(3, 6)
        self.repl_block_tests(new_region)

        print("... saving ...")
        new_region.save(target_dir + "/" + filename)
        print("... finished")

    def air_block_tests(self, new_region: anvil.EmptyRegion):
        """Adds test cubes for all thicknesses to the passed region.

        Parameters
        ----------
        new_region : anvil.EmptyRegion
            The region the tests should be added to
        max_thickness : int, optional
            The maximum thickness a test should have
        """
        self.air = anvil.Block("minecraft", "air")

        for width in range(self.pos.max_width, self.pos.min_width - 1, -1):
            # TODO use shape based approach?
            for size in range(1, width - 1):
                for ID in solid_blocks + all_transparent_blocks:
                    b = anvil.Block("minecraft", ID)
                    self.set_air_cube(new_region, b, width, size)

                    self.pos.next_pos()
                self.pos.next_z()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def get_shape(self, dim_size: int, num_blocks: int=-1):
        # TODO or num_blocks == 3
        if num_blocks == -1 or num_blocks == 3:
            num_blocks = dim_size * dim_size * dim_size
        return self.shape_generator.get_shape(dim_size, num_blocks)

    def water_block_tests(self, new_region: anvil.EmptyRegion):
        self.water = anvil.Block("minecraft", "water")
        self.glass = anvil.Block("minecraft", "glass")
        self.stone = anvil.Block("minecraft", "stone")

        for num_blocks in range(self.pos.max_width - 4, self.pos.min_width - 1 - 4, -1):
            for shape in self.get_shape(num_blocks, num_blocks):
                for ID in solid_blocks + all_transparent_blocks:
                    b = anvil.Block("minecraft", ID)
                    self.set_water_cube(new_region, b, num_blocks, shape)

                    self.pos.next_pos()
                self.pos.next_z()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def repl_block_tests(self, new_region):
        for num_blocks in range(self.pos.max_width, self.pos.min_width - 1, -1):
            for ID in solid_blocks + all_transparent_blocks:
                b = anvil.Block("minecraft", ID)
                self.set_solid_cube(new_region, b)

                self.pos.next_pos()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def set_air_cube(self, region: anvil.EmptyRegion, block: anvil.Block, thickness, size):
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # TODO use halfwidth from self.pos
        left = int(thickness / 2.0)
        right = left
        if thickness % 2 == 0:
            right = right - 1
        for i in range(-left, right + 1):
            for j in range(-left, right + 1):
                for k in range(-left, right + 1):
                    region.set_block(block, x + i, y + j, z + k)

        left = int(size / 2.0)
        right = left
        if size % 2 == 0:
            right = right - 1
        for i in range(-left, right + 1):
            for j in range(-left, right + 1):
                for k in range(-left, right + 1):
                    region.set_block(self.air, x + i, y + j, z + k)

    def set_water_cube(self, region: anvil.EmptyRegion, block: anvil.Block, num_blocks, shape):
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # TODO use halfwidth from self.pos
        # inside dimensions
        i_left = int(num_blocks / 2.0)
        i_right = i_left
        # total dimensions
        left = i_left + 2
        right = left

        if num_blocks % 2 == 0:
            right = right - 1
            i_right = i_right - 1

        for i in range(-left, right + 1):
            for k in range(-left, right + 1):
                region.set_block(self.stone, x + i, y - left, z + k)
                region.set_block(self.stone, x + i, y - left - 1, z + k)

        for j in range(-left + 1, right):
            for i in range(-left, right + 1):
                region.set_block(self.glass, x + i, y + j, z - left)
                region.set_block(self.glass, x + i, y + j, z + right)

            for k in range(-left, right + 1):
                region.set_block(self.glass, x - left, y + j, z + k)
                region.set_block(self.glass, x + right, y + j, z + k)

        for i in range(-i_left - 1, i_right + 2):
            for j in range(-i_left - 1, i_right + 2):
                for k in range(-i_left - 1, i_right + 2):
                    region.set_block(self.water, x + i, y + j, z + k)

        # TODO this should be the same value as num_blocks
        size = len(shape)
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if shape[i][j][k] == 1:
                        region.set_block(block, x + i - i_left, y + j - i_left, z + k - i_left)

    def set_solid_cube(self, region: anvil.EmptyRegion, block: anvil.Block):
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # TODO use halfwidth from self.pos
        right = int(self.pos.now_width / 2.0)
        left = -right
        if self.pos.now_width % 2 == 0:
            right = right - 1
        for i in range(left, right + 1):
            for j in range(left, right + 1):
                for k in range(left, right + 1):
                    region.set_block(block, x + i, y + j, z + k)

###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    c = TestMapCreator()
    c.create_test_map()
