# https://realpython.com/python-application-layouts/
# https://realpython.com/python-modules-packages/
# https://github.com/navdeep-G/samplemod
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
import os
import sys
import unittest

import anvil  # minecraft import
from tkinter import Tk  # Needed for metainfo

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import config as cfg
from copier import Copier
from meta_information import MetaInformation


class TestAll(unittest.TestCase):
    def test_copy(self):
        # Tests
        Tk()
        meta_info = MetaInformation()
        S_DIR = os.path.dirname(os.path.abspath(__file__)) + "/region_files"
        meta_info.set_dirs(S_DIR + "_original", S_DIR + "_replacement", S_DIR + "_copy")
        meta_info.finished = False

        settings_list = [[1, 0, 0, 1, 1, 1]]

        c = Copier(meta_info)

        for setting in settings_list:
            # Set the meta_info data
            meta_info.air_pockets.set(setting[0])
            meta_info.water_blocks.set(setting[1])
            meta_info.repl_blocks.set(setting[2])
            meta_info.apocket_size.set(setting[3])
            meta_info.wpocket_size.set(setting[4])
            meta_info.repl_area.set(setting[5])

            # Run the copy process
            c.run()

            while not meta_info.text_queue.empty():
                print(meta_info.text_queue.get(0))

            self.assertTrue(os.path.exists(meta_info.target_dir.get()))
            self.assertTrue(self.are_files_equal(S_DIR))

        # TODO this is used to trigger an error in the testing
        # a better way would be to print directly to the github log instead of the stdout
        # self.assertEqual(2, 3)

        # IMPORTANT
        # TODO this does not work with the tests since this function does not exist in the lib
        # new_chunk.set_data(chunk.data)

        # TODO push test map and result map

    def are_files_equal(self, S_DIR):
        # TODO get the files
        filename = "r.0.0.mca"
        region = anvil.Region.from_file(S_DIR + "_copy" + "/" + filename)
        cmp_region = anvil.Region.from_file(S_DIR + "_test" + "/" + filename)

        for chunk_x in range(cfg.REGION_C_X):
            for chunk_z in range(cfg.REGION_C_Z):
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                cmp_chunk = anvil.Chunk.from_region(cmp_region, chunk_x, chunk_z)

                x = 0
                y = 0
                z = 0

                for block in chunk.stream_chunk():
                    cmp_block = cmp_chunk.get_block(x, y, z)

                    if cmp_block.id != block.id:
                        return False

                    # TODO
                    if z == 15 and x == 15:
                        y += 1
                    if x == 15:
                        z = (z + 1) % 16
                    x = (x + 1) % 16

        return True
