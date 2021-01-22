import random

import math_helper as m_hp
import numpy as np


def compare_unsigned(x: int, y: int):
    if abs(x) < abs(y):
        return -1
    elif abs(y) < abs(x):
        return 1
    else:
        return 0


def lowest_one_bit(x: int):
    b = (x & -x).bit_length()
    return 1 << (b - 1)


def number_trailing_zeros(x: int):
    count = 0
    while (x & 1) == 0:
        x = x >> 1
        count += 1

    return count


class IntBuilder:
    def __init__(self, size: int = 4):
        if size > 4:
            raise ValueError("To many combinations for random.sample().")

        # A lookup table to see how many combinations preceeded this one
        self.size = size * size * size
        self.lookup_table_combination_pos = np.zeros((self.size, self.size))
        # The number of possible combinations with i bits
        self.nbr_combinations = np.zeros(self.size + 1)
        self.init()

    def get_all_bits_set(self, len: int):
        return (1 << len) - 1

    def get_next_combination(self, last_i: int):
        """
        https://graphics.stanford.edu/~seander/bithacks.html#NextBitPermutation
        """
        tmp = (last_i | (last_i - 1)) + 1
        next_i = tmp | ((int((tmp & -tmp) / (last_i & -last_i)) >> 1) - 1)
        return next_i

    def init(self):
        for bit in range(self.size):
            # Ignore less significant bits, compute how many combinations have to be
            # visited to set this bit, i.e.
            # (bit = 4, pos = 5), before came 0b1XXX and 0b1XXXX, that's C(3, 3) + C(4, 3)
            nbrBefore = 0
            # The nth-bit can be only encountered after pos n
            for pos in range(bit, self.size):
                self.lookup_table_combination_pos[bit][pos] = nbrBefore
                nbrBefore += m_hp.n_choose_r(pos, bit)

        for bits in range(self.size + 1):
            self.nbr_combinations[bits] = m_hp.n_choose_r(self.size, bits)
            # Important for modulo check. Otherwise we must use unsigned arithmetic
            assert self.nbr_combinations[bits] > 0

    def get_combination_n(self, start: int, n: int):
        """
        https://stackoverflow.com/questions/46693944/find-nth-int-with-10-set-bits
        """
        # Get the position of the current pattern start
        nbrBits = 0
        position = 0

        while start != 0:
            currentBit = lowest_one_bit(start)  # start & -start
            bitPos = number_trailing_zeros(currentBit)
            position += self.lookup_table_combination_pos[nbrBits][bitPos]
            # toggle off bit
            start ^= currentBit
            nbrBits += 1

        position += n
        # Wrapping, optional
        position %= self.nbr_combinations[nbrBits]

        # And reverse lookup
        v = 0
        m = self.size - 1
        while nbrBits > 0:
            nbrBits -= 1
            bitPositions = self.lookup_table_combination_pos[nbrBits]
            # Search for largest bitPos such that position >= bitPositions[bitPos]
            while compare_unsigned(position, bitPositions[m]) < 0:
                m -= 1
            position -= bitPositions[m]
            v ^= 0b1 << m
            m -= 1

        return v

    def get_all_combs_n_bits(self, bits: int, n: int):
        shape_list = []

        # Calculate the amount of possible combinations
        comb_count = m_hp.n_choose_r(bits, n)
        # Create first entry
        last_i = self.get_all_bits_set(n)
        shape_list.append(last_i)
        next_i = 0
        # Create all entries in between
        for i in range(1, comb_count):
            next_i = self.get_next_combination(last_i)
            shape_list.append(next_i)
            last_i = next_i

        return shape_list

    def get_k_combs_n_bits(self, bits: int, n: int, k: int = -1):
        """ Returns a list of k integers that have n bits set
        """
        shape_list = []
        if n > bits:
            raise Exception("More blocks then positions!")
        if bits > self.size:
            raise Exception("To many combinations for random.sample(). (to many bits)")

        # Calculate the amount of possible combinations
        comb_count = m_hp.n_choose_r(bits, n)

        if k == 0:
            return []
        elif k < 0 or k > comb_count:
            k = comb_count

        # Collect the combinations that should be saved
        selected = random.sample(range(comb_count), k)
        selected.sort()

        start = self.get_all_bits_set(n)
        for idx in selected:
            shape_list.append(self.get_combination_n(start, idx))

        return shape_list


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    i = IntBuilder()
    print(i.get_combination_n(0b1, 1))
    assert i.get_combination_n(0b1, 1) == 2
    print(i.get_combination_n(0b11, 1))
    assert i.get_combination_n(0b11, 1) == 5
    print(i.get_combination_n(0b111, 1))
    assert i.get_combination_n(0b111, 1) == 11
    print(i.get_combination_n(0b1111111111, 1))
    assert i.get_combination_n(0b1111111111, 1) == 1535

    print(i.get_all_bits_set(1))
    assert i.get_all_bits_set(1) == 1
    print(i.get_all_bits_set(2))
    assert i.get_all_bits_set(2) == 3
    print(i.get_all_bits_set(3))
    assert i.get_all_bits_set(3) == 7
