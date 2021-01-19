import operator as op
import numpy as np
from functools import reduce


def n_choose_r(n: int, r: int):
    """
    https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
    """
    r = min(r, n - r)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer // denom


def gauss_curve_integral_1(pos: int, max_val: int):
    """
    https://en.wikipedia.org/wiki/Gaussian_function
    """
    center = max_val / 2
    std_dev = max_val / 8
    # Used to generate an integral of 1
    height = 1 / (std_dev * np.sqrt(2 * np.pi))

    return height * np.exp(-np.power(pos - center, 2) / (2 * np.power(std_dev, 2)))
