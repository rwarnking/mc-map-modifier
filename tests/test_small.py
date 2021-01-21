import os
import unittest

from test_utils import TestUtils


class TestSmall(unittest.TestCase):
    def test_run(self):
        settings_list = [1, 1, 1, 1, 1, 1]
        S_DIR = os.path.dirname(os.path.abspath(__file__)) + "/region_files"

        t_u = TestUtils()
        t_u.copy(S_DIR, settings_list)

        self.assertTrue(os.path.exists(S_DIR + "_copy"))
        self.assertTrue(t_u.are_files_equal(S_DIR))
