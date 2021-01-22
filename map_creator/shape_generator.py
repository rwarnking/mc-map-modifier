import math

from integer import IntBuilder


class ShapeGenerator:
    def __init__(self):
        self.int_builder = IntBuilder()

    def convert_i_to_shape(self, input: int, bits: int, dim_size: int):
        # Bitshift is used since there may be faster then calling math.pow
        # https://stackoverflow.com/questions/12556906/
        arr = [0] * bits
        for shift in range(bits):
            arr[bits - 1 - shift] = (input & 1 << shift) >> shift

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

    def get_shapes(self, dim_size: int, num_blocks: int):
        if num_blocks < 1:
            raise Exception("num_blocks must be greater than 0")

        bits = dim_size * dim_size * dim_size
        int_list = self.int_builder.get_all_combs_n_bits(bits, num_blocks)
        return [self.convert_i_to_shape(i, bits, dim_size) for i in int_list]

    def get_n_shapes(self, dim_size: int, num_blocks: int, n: int):
        if num_blocks < 1:
            raise Exception("num_blocks must be greater than 0")

        bits = dim_size * dim_size * dim_size

        if num_blocks == bits:
            i = self.int_builder.get_all_bits_set(bits)
            return [self.convert_i_to_shape(i, bits, dim_size)]

        int_list = self.int_builder.get_k_combs_n_bits(bits, num_blocks, n)
        return [self.convert_i_to_shape(i, bits, dim_size) for i in int_list]

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
    this_list = sg.get_n_shapes(1, 1, 1)
    sg.print_shapes(this_list)
    print("################")
    this_list = sg.get_n_shapes(2, 2, 0)
    sg.print_shapes(this_list)
    print("################")
    this_list = sg.get_n_shapes(2, 2, 4)
    sg.print_shapes(this_list)
    print("################")
    this_list = sg.get_n_shapes(2, 2, 28)
    sg.print_shapes(this_list)
    print("################")
    this_list = sg.get_n_shapes(3, 10, 6)
    sg.print_shapes(this_list)
    print("################")
    this_list = sg.get_n_shapes(4, 7, 6)
    sg.print_shapes(this_list)
