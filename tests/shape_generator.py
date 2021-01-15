import math
import random
import helper as hp


class ShapeGenerator:
    def __init__(self):
        self.shape_dict = {}

    def convert(self, arr, dim_size: int):
        arr_x = []
        arr_y = []
        arr_z = []
        half = math.pow(dim_size, 2)

        for i in range(len(arr)):
            arr_x.append(arr[i])
            if i % dim_size == dim_size - 1:
                arr_y.append(arr_x)
                arr_x = []
            if i % half == half - 1:
                arr_z.append(arr_y)
                arr_y = []
        return arr_z

    def generate_n_shapes_n_blocks(self, dim_size: int, num_blocks: int, num: int = -1):
        shape_list = []
        bits = dim_size * dim_size * dim_size
        if num_blocks > bits:
            raise Exception("More blocks then positions!")
        if dim_size > 4:
            print("This is a lot of data.")

        # Calculate the amount of possible combinations
        comb_count = hp.n_choose_r(bits, num_blocks)
        # Mark the combinations that should be saved
        selected = [False] * comb_count
        if num < 0:
            num = comb_count
        for e in random.sample(range(comb_count), num):
            selected[e] = True

        # https://graphics.stanford.edu/~seander/bithacks.html#NextBitPermutation
        last_i = 0
        next_i = 0
        end = 0
        arr = [0] * bits

        # Create first entry
        for i in range(num_blocks):
            last_i = last_i + (1 << i)
        # Add first entry
        if selected[0] == True:
            # TODO add this to convert function
            for shift in range(bits):
                arr[bits - 1 - shift] = (last_i & 1 << shift) >> shift
            shape_list.append(self.convert(arr, dim_size))

        # Create all entries in between
        for i in range(1, comb_count):
            arr = [0] * bits
            tmp = (last_i | (last_i - 1)) + 1
            next_i = tmp | ((int((tmp & -tmp) / (last_i & -last_i)) >> 1) - 1)

            # TODO determine max amount of combinations, then use an array of random numbers
            # to decide wether to select an element or not
            if selected[i] == True:
                for shift in range(bits):
                    arr[bits - 1 - shift] = (next_i & 1 << shift) >> shift
                shape_list.append(self.convert(arr, dim_size))
            if len(shape_list) == num:
                break;
            last_i = next_i

        return shape_list

    def generate_all_shapes(self, dim_size):
        shape_list = []
        bits = dim_size * dim_size * dim_size
        if dim_size == 3:
            print("Estimated time: atleast three minutes!")
        if dim_size > 3:
            raise Exception("This number is to high! The program would need years to finish.")

        # Bitshift is used since there may be faster then calling math.pow
        # https://stackoverflow.com/questions/12556906/
        for i in range(1 << bits):
            arr = [0] * bits
            for shift in range(bits):
                arr[shift] = (i & 1 << shift) >> shift
            shape_list.append(self.convert(arr, dim_size))

        return shape_list

    def get_shapes(self, dim_size: int, num_blocks: int):
        key = f"{dim_size}-{num_blocks}"
        if key not in self.shape_dict:
            self.shape_dict[key] = self.generate_n_shapes_n_blocks(dim_size, num_blocks)
        return self.shape_dict[key]

    def get_n_shapes(self, dim_size: int, num_blocks: int, n: int):
        if num_blocks < 1:
            raise Exception("num_blocks must be greater than 0")

        key = f"{dim_size}-{num_blocks}"
        if key not in self.shape_dict:
            self.shape_dict[key] = self.generate_n_shapes_n_blocks(dim_size, num_blocks, n)
        else:
            print("already there")
        return self.shape_dict[key]

    def clear(self):
        self.shape_dict.clear()

    def print_shapes(self, shapes):
        for shape in shapes:
            print(shape)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    sg = ShapeGenerator()
    print("################")
    this_list = sg.get_shapes(2, 2)
    sg.print_shapes(this_list)
    print("################")
    sg.clear()
    this_list = sg.get_n_shapes(1, 1, 1)
    sg.print_shapes(this_list)
    print("################")
    sg.clear()
    this_list = sg.get_n_shapes(2, 2, 0)
    sg.print_shapes(this_list)
    print("################")
    sg.clear()
    this_list = sg.get_n_shapes(2, 2, 4)
    sg.print_shapes(this_list)
    print("################")
    sg.clear()
    this_list = sg.get_n_shapes(3, 10, 6)
    sg.print_shapes(this_list)
