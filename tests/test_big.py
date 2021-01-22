import os
import unittest

from test_utils import TestUtils


class TestBig(unittest.TestCase):
    def test_run(self):
        settings_list = [1, 1, 1, 1, 1, 1]
        S_DIR = os.path.dirname(os.path.abspath(__file__)) + "/region_files"

        test_num = "t2"
        t_u = TestUtils()
        t_u.copy(S_DIR, test_num, settings_list)

        self.assertTrue(os.path.exists(S_DIR + "_copy/" + test_num))
        self.assertTrue(t_u.are_files_equal(S_DIR, test_num))
