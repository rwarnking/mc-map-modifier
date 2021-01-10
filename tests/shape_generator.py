import math


class ShapeGenerator:
    def __init__(self):
        self.shape_dict = {}

    def convert(self, arr, dim_size):
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

    def generate_shapes(self, num_blocks, dim_size):
        shape_list = []
        bits = dim_size * dim_size * dim_size
        if num_blocks > bits:
            raise Exception("More blocks then positions!")
        if dim_size == 3:
            print("Estimated time: atleast three minutes!")
        if dim_size > 3:
            raise Exception("This number is to high! The program need more than 584942 years to finish.")

        # Bitshift is used since there may be faster then calling math.pow
        # https://stackoverflow.com/questions/12556906/
        for i in range(1 << bits):
            a = 0
            arr = [0] * bits
            for shift in range(bits):
                arr[shift] = ((i & 1 << shift) >> shift)
                a = a + arr[shift]
                if a > num_blocks:
                    break;
            if a == num_blocks:
                shape_list.append(self.convert(arr, dim_size))

        return shape_list

    def get_shape(self, num_blocks, dim_size):
        key = f"{num_blocks}-{dim_size}"
        if key not in self.shape_dict:
            self.shape_dict[key] = self.generate_shapes(num_blocks, dim_size)
        return self.shape_dict[key]

    def print_shapes(self, shapes):
        for shape in shapes:
            print(shape)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    sg = ShapeGenerator()
    l = sg.get_shape(2, 2)
    sg.print_shapes(l)
