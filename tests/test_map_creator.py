import pathmagic  # noqa isort:skip
import os
from typing import Callable, List

import anvil  # minecraft import
import config as cfg  # own import
import math_helper as m_hp
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

    def add_arr(self, arr: List[int]):
        self.x += arr[0]
        self.y += arr[1]
        self.z += arr[2]

    def add_ints(self, x: int, y: int, z: int):
        self.x += x
        self.y += y
        self.z += z

    def print(self):
        print(self.x, self.y, self.z)


class BlockPosition:
    def __init__(self, min_w: int, max_w: int, r_x: int = 0, r_z: int = 0, xyz: Vector = None):
        self.r_x = r_x * cfg.REGION_B_X
        self.r_z = r_z * cfg.REGION_B_Z

        self.dist = 1
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()

        if xyz is None:
            self.xyz = Vector.from_one_val(self.half_width + self.dist)
        else:
            self.xyz = xyz
        self.xyz.add_ints(self.r_x, 0, self.r_z)

    def reset_no_y(self, min_w: int, max_w: int):
        self.min_width = min_w
        self.max_width = max_w
        self.now_width = max_w
        self.update_width()
        self.xyz = Vector(
            self.half_width + self.dist + self.r_x,
            self.xyz.y,
            self.half_width + self.dist + self.r_z,
        )
        self.next_y()

    def increase_width(self, amount: int = 1):
        self.decrease_width(amount)

    def decrease_width(self, amount: int = -1):
        self.now_width += amount
        self.update_width()

    def update_width(self):
        self.half_width = int(self.now_width / 2)
        dist = self.now_width + self.half_width + self.dist + self.dist + 1 + 1
        self.limit = Vector(
            cfg.REGION_B_X - dist + self.r_x,
            cfg.REGION_B_Y - dist,
            cfg.REGION_B_Z - dist + self.r_z,
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
        self.xyz.x = self.half_width + self.dist + self.r_x
        self.xyz.y += self.now_width + self.dist
        self.xyz.z = self.half_width + self.dist + self.r_z

        if add and self.now_width % 2 == 0:
            self.xyz.y += 1
        if self.xyz.y > self.limit.y:
            raise Exception("Y border value reached!")

    def next_z(self):
        self.xyz.x = self.half_width + self.dist + self.r_x
        self.xyz.z += self.now_width + self.dist


class TestMapCreator:
    def __init__(self):
        self.shape_generator = ShapeGenerator()

        self.air = anvil.Block("minecraft", "air")
        self.water = anvil.Block("minecraft", "water")
        self.glass = anvil.Block("minecraft", "glass")
        self.stone = anvil.Block("minecraft", "stone")

    def create_test_map(self, filename: str, cube_widths: List[List[int]]):
        self.set_cube_width(cube_widths)

        print(f"running ... {filename}")
        target_dir = os.path.dirname(os.path.abspath(__file__)) + "/region_files_original"
        end = filename.split(".")
        r_x = int(end[1])
        r_z = int(end[2])

        self.pos = BlockPosition(
            self.min_max_cube_width[0][0], self.min_max_cube_width[0][1], r_x, r_z
        )

        # Create a new region with the `EmptyRegion` class at region coords
        new_region = anvil.EmptyRegion(r_x, r_z)
        # Fill region with empty chunks
        for cx in range(0, 32):
            for cz in range(0, 32):
                chunk = anvil.EmptyChunk(cx, cz)
                new_region.add_chunk(chunk)

        print("... generating airblock tests ...")
        set_func = self.set_air_cube
        self.set_test_blocks(new_region, set_func, 2)
        print("... generating waterblock tests ...")
        self.pos.reset_no_y(self.min_max_cube_width[1][0], self.min_max_cube_width[1][1])
        set_func = self.set_water_cube
        self.set_test_blocks(new_region, set_func, 4)
        print("... generating replblock tests ...")
        self.pos.reset_no_y(self.min_max_cube_width[2][0], self.min_max_cube_width[2][1])
        set_func = self.set_solid_cube
        self.set_test_blocks(new_region, set_func)

        print("... saving ...")
        new_region.save(target_dir + "/" + filename)
        print("... finished")

    def set_cube_width(self, cube_widths: List[List[int]]):
        # Array with the cube width values for all test stages
        self.min_max_cube_width = cube_widths
        # Calculate total expected height
        self.total_height = 0
        for mm in self.min_max_cube_width:
            # Add the distance between the tests
            self.total_height += mm[1]
            for h in range(mm[0], mm[1] + 1):
                self.total_height += h + 1

    def set_test_blocks(
        self,
        new_region: anvil.EmptyRegion,
        cube_func: Callable[[anvil.EmptyRegion, anvil.Block, List[List[List[int]]]], None],
        adj_w: int = 0,
    ):
        """Adds test cubes for all thicknesses to the passed region.

        Parameters
        ----------
        new_region : anvil.EmptyRegion
            The region the tests should be added to
        cube_func : Callable[[anvil.EmptyRegion, anvil.Block, List[List[List[int]]]]
            The function responsible for placing the cubes
        adj_w : int, optional
            Adjustment of the width to allow for layers of blocks around the shapes
        """
        for width in range(self.pos.max_width - adj_w, self.pos.min_width - 1 - adj_w, -1):
            for shape in self.get_shapes(width):
                for ID in solid_blocks + transparent_blocks:
                    b = anvil.Block("minecraft", ID)
                    cube_func(new_region, b, shape)

                    self.pos.next_pos()
                self.pos.next_z()
            self.pos.decrease_width()
            self.pos.next_y(True)

    def get_shapes(self, dim_size: int, num_blocks: int = -1):
        if num_blocks == -1:
            # TODO
            layer = min(int(cfg.REGION_B_Y / self.total_height), 3)
            max_elems = cfg.REGION_B_X * cfg.REGION_B_Z
            max_elems /= (self.pos.now_width + 1) * (self.pos.now_width + 1)
            max_elems /= len(solid_blocks) + len(transparent_blocks)
            max_elems *= layer

            count = dim_size * dim_size * dim_size
            shapes = self.shape_generator.get_n_shapes(dim_size, count, 1)

            if dim_size < 5:
                for i in range(1, count):
                    # Get the amount of elems that should be used for this shapetype
                    # Uses normal distribution and does not produce more than max_elems
                    # TODO is not jet optimal since the total elem count is not equal to max_elems
                    elems = int(m_hp.gauss_curve_integral_1(i, count) * max_elems)
                    shapes += self.shape_generator.get_n_shapes(dim_size, i, elems)
            return shapes

        if num_blocks > 2:
            elems = (cfg.REGION_B_X * cfg.REGION_B_Z) / (self.pos.now_width + 1)
            return self.shape_generator.get_n_shapes(dim_size, num_blocks, elems)

        return self.shape_generator.get_shapes(dim_size, num_blocks)

    def set_air_cube(self, region: anvil.EmptyRegion, block: anvil.Block, shape):
        assert len(shape) == len(shape[0]) and len(shape[0]) == len(shape[0][0])
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z

        # total dimensions
        right = self.pos.half_width
        left = -right
        # inside dimensions
        i_right = right - 1
        i_left = -i_right

        if self.pos.now_width % 2 == 0:
            right -= 1
            i_right -= 1

        for i in range(left, right + 1):
            for j in range(left, right + 1):
                for k in range(left, right + 1):
                    region.set_block(block, x + i, y + j, z + k)

        self.set_shape(region, self.air, shape, range(i_left, i_right + 1))

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
            right -= 1
            i_right -= 1

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

        self.set_shape(region, block, shape, range(i_left, i_right + 1))

    def set_solid_cube(self, region: anvil.EmptyRegion, block: anvil.Block, shape):
        assert len(shape) == len(shape[0]) and len(shape[0]) == len(shape[0][0])

        right = self.pos.half_width
        left = -right
        if self.pos.now_width % 2 == 0:
            right -= 1
        self.set_shape(region, block, shape, range(left, right + 1))

    def set_shape(self, region: anvil.EmptyRegion, block: anvil.Block, shape, _range):
        x, y, z = self.pos.xyz.x, self.pos.xyz.y, self.pos.xyz.z
        for i in _range:
            for j in _range:
                for k in _range:
                    if shape[i][j][k] == 1:
                        region.set_block(block, x + i, y + j, z + k)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    c = TestMapCreator()
    # c.create_test_map("r.0.0.mca", [[3, 3], [5, 5], [3, 3]])
    c.create_test_map("r.0.0.mca", [[3, 6], [5, 7], [3, 6]])
    # c.create_test_map("r.-1.0.mca", [[3, 6], [5, 7], [3, 6]])
