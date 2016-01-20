__author__ = 'aishimaj'

from utils import replace_top_directory_level

import unittest

class TestReplaceTopDirectoryLevel(unittest.TestCase):
    def test1(self):
        test_dir = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
        data_dir = "/sans/60days"
        result = replace_top_directory_level(test_dir, data_dir)
        self.assertTrue(result == "/sans/60days/10123g/frames/calibration/test_crystal/testcrystal_1_180.img")

    def test2(self):
        test_dir = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
        data_dir = "/sans/60days/"
        with self.assertRaises(ValueError):
            result = replace_top_directory_level(test_dir, data_dir)

    def test3(self):
        test_dir  = "/data/home/10123g/calibration/test_crystal/testcrystal_1_180.img"
        data_dir = "/sans/60days"
        result = replace_top_directory_level(test_dir, data_dir)
        self.assertTrue(result == "/sans/60days/10123g/home/calibration/test_crystal/testcrystal_1_180.img")

    def test4(self):
        test_dir  = "/data/home/MX1cal20150115k/calibration/test_crystal/testcrystal_1_180.img"
        data_dir = "/sans/60days"
        result = replace_top_directory_level(test_dir, data_dir)
        self.assertTrue(result == "/sans/60days/MX1cal20150115k/home/calibration/test_crystal/testcrystal_1_180.img")

if __name__ == '__main__':
    unittest.main()