from utils import create_auto_dir_from_last_frame
import unittest

__author__ = 'aishimaj'


class TestCreateAutoDir(unittest.TestCase):
    def test1(self):
        dirname = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(create_auto_dir_from_last_frame(dirname), "/data/10123g/home/calibration/auto")

    def test2(self):
        dirname = "/data/home/10123g/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(create_auto_dir_from_last_frame(dirname), "/data/10123g/home/calibration/auto")

    def test3(self):
        dirname = "/sans/60days/home/10123g/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(create_auto_dir_from_last_frame(dirname), "/sans/60days/10123g/home/calibration/auto")

    def test3(self):
        dirname = "/sans/60days/home/MX1cal20150115k/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(create_auto_dir_from_last_frame(dirname), "/sans/60days/MX1cal20150115k/home/calibration/auto")

if __name__ == '__main__':
    unittest.main()