import os
import sys

import anvil  # minecraft import

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import config as cfg  # own import
from block_tests import solid_blocks, transparent_blocks
from shape_generator import ShapeGenerator


class Vector:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_one_val(cls, val: int):
        return cls(val, val, val)

    @classmethod
    def from_array(cls, xyz: [int]):
        return cls(xyz[0], xyz[1], xyz[2])

    def add_vec(self, vec: "Vector"):
        self.x += vec.x
        self.y += vec.y
        self.z += vec.z


class BlockPosition:
    def __init__(self, min_w: int, max_w: int, xyz: Vector = None):
        self.dist = 1
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()

        if xyz is None:
            self.xyz = Vector.from_one_val(self.half_width + 1)
        else:
            self.xyz = xyz

    def reset_no_y(self, min_w: int, max_w: int):
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()
        self.xyz = Vector(self.half_width + 1, self.xyz.y, self.half_width + 1)
        self.next_y()

    def increase_width(self, amount: int = 1):
        self.decrease_width(amount)

    def decrease_width(self, amount: int = -1):
        self.now_width += amount
        self.update_width()

    def update_width(self):
        self.half_width = int(self.now_width / 2)
        self.limit = Vector(
            cfg.REGION_B_X - self.now_width - self.half_width - self.dist - 1,
            cfg.REGION_B_Y - self.now_width - self.half_width - self.dist - 1,
            cfg.REGION_B_Z - self.now_width - self.half_width - self.dist - 1,
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

    def next_y(self, add: bool = False):
        self.xyz.x = self.half_width + self.dist
        self.xyz.y += self.now_width + self.dist
        self.xyz.z = self.half_width + self.dist

        if add and self.now_width % 2 == 0:
            self.xyz.y += 1
        if self.xyz.y > self.limit.y:
            raise Exception("Y border value reached!")

    def next_z(self):
        self.xyz.x = self.half_width + self.dist
        self.xyz.z += self.now_width + self.dist


class TestMapCreator:
    def __init__(self):
        self.shape_generator = ShapeGenerator()
        min_cube_width = 3
        max_cube_width = 6
        self.pos = BlockPosition(min_cube_width, max_cube_width)

    def create_test_map(self, filename: str = "r1.0.0.mca"):
        print("running ...")
        target_dir = os.path.dirname(os.path.abspath(__file__)) + "/region_files_original"
        end = filename.split(".")
        r_x = int(end[1])
        r_z = int(end[2])

        # Create a new region with the `EmptyRegion` class at region coords
        new_region = anvil.EmptyRegion(r_x, r_z)

        print("... generating airblock tests ...")
        self.air_block_tests(new_region)
        print("... generating waterblock tests ...")
        self.pos.reset_no_y(5, 7)
        self.water_block_tests(new_region)
        print("... generating replblock tests ...")
        self.pos.reset_no_y(3, 6)
        self.repl_block_tests(new_region)

        print("... saving ...")
        new_region.save(target_dir + "/" + filename)
        print("... finished")

    def get_shapes(self, dim_size: int, num_blocks: int = -1):
        if num_blocks == -1:
            # TODO
            max_elems = cfg.REGION_B_X * cfg.REGION_B_Z
            max_elems /= (self.pos.now_width + 1) * (self.pos.now_width + 1)
            max_elems /= len(solid_blocks) + len(transparent_blocks)
            count = dim_size * dim_size * dim_size
            shapes = self.shape_generator.get_n_shapes(dim_size, count, 1)
            for i in range(2, count):
                # Get smthg similar to gaus distribution by calculating the percentage and
                # converting it to a [-0.5, 0.5] range and then to a [0, 0.5, 0] range
                percent = -abs((i / count) - 0.5) + 0.5
                elems = int(max(percent * percent * max_elems, 1.0))
                # elems calculation does not sum up to max_elems
                shapes += self.shape_generator.get_n_shapes(dim_size, i, elems)
            return shapes

        if num_blocks > 2:
            elems = (cfg.REGION_B_X * cfg.REGION_B_Z) / (self.pos.now_width + 1)
            return self.shape_generator.get_n_shapes(dim_size, num_blocks, elems)

        return self.shape_generator.get_shapes(dim_size, num_blocks)

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
            for shape in self.get_shapes(width - 2):
                for ID in solid_blocks + transparent_blocks:
                    b = anvil.Block("minecraft", ID)
                    self.set_air_cube(new_region, b, shape)

                    self.pos.next_pos()
                self.pos.next_z()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def water_block_tests(self, new_region: anvil.EmptyRegion):
        self.water = anvil.Block("minecraft", "water")
        self.glass = anvil.Block("minecraft", "glass")
        self.stone = anvil.Block("minecraft", "stone")

        for inner_width in range(self.pos.max_width - 4, self.pos.min_width - 1 - 4, -1):
            for shape in self.get_shapes(inner_width):
                for ID in solid_blocks + transparent_blocks:
                    b = anvil.Block("minecraft", ID)
                    self.set_water_cube(new_region, b, shape)

                    self.pos.next_pos()
                self.pos.next_z()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def repl_block_tests(self, new_region):
        for num_blocks in range(self.pos.max_width, self.pos.min_width - 1, -1):
            for ID in solid_blocks + transparent_blocks:
                b = anvil.Block("minecraft", ID)
                self.set_solid_cube(new_region, b)

                self.pos.next_pos()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def set_air_cube(self, region: anvil.EmptyRegion, block: anvil.Block, shape):
        assert len(shape) == len(shape[0]) and len(shape[0]) == len(shape[0][0])
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # total dimensions
        right = self.pos.half_width
        left = -right
        # inside dimensions
        i_left = -(right - 1)

        if self.pos.now_width % 2 == 0:
            right = right - 1

        for i in range(left, right + 1):
            for j in range(left, right + 1):
                for k in range(left, right + 1):
                    region.set_block(block, x + i, y + j, z + k)

        # TODO improvements? => remove size, dont use multiple ranges, calc x + i + i_left once
        size = len(shape)
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if shape[i][j][k] == 1:
                        region.set_block(self.air, x + i + i_left, y + j + i_left, z + k + i_left)

    def set_water_cube(self, region: anvil.EmptyRegion, block: anvil.Block, shape):
        assert len(shape) == len(shape[0]) and len(shape[0]) == len(shape[0][0])
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # total dimensions
        right = self.pos.half_width
        left = -right
        # inside dimensions
        i_right = right - 2
        i_left = -i_right

        if self.pos.now_width % 2 == 0:
            right = right - 1
            i_right = i_right - 1

        for i in range(left, right + 1):
            for k in range(left, right + 1):
                region.set_block(self.stone, x + i, y + left, z + k)
                region.set_block(self.stone, x + i, y + left - 1, z + k)

        for j in range(left + 1, right):
            for i in range(left, right + 1):
                region.set_block(self.glass, x + i, y + j, z + left)
                region.set_block(self.glass, x + i, y + j, z + right)

            for k in range(left, right + 1):
                region.set_block(self.glass, x + left, y + j, z + k)
                region.set_block(self.glass, x + right, y + j, z + k)

        for i in range(i_left - 1, i_right + 2):
            for j in range(i_left - 1, i_right + 2):
                for k in range(i_left - 1, i_right + 2):
                    region.set_block(self.water, x + i, y + j, z + k)

        # TODO improvements? => remove size, dont use multiple ranges, calc x + i + i_left once
        size = len(shape)
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if shape[i][j][k] == 1:
                        region.set_block(block, x + i + i_left, y + j + i_left, z + k + i_left)

    def set_solid_cube(self, region: anvil.EmptyRegion, block: anvil.Block):
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        right = self.pos.half_width
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
