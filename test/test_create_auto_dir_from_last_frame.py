from utils import create_auto_dir_from_last_frame
import unittest

__author__ = 'aishimaj'


class TestCreateAutoDir(unittest.TestCase):
    def test1(self):
        dirname = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(create_auto_dir_from_last_frame(dirname), "/data/10123g/home/calibration/auto")

if __name__ == '__main__':
    unittest.main()