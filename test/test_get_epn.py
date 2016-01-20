from utils import get_epn
import unittest

__author__ = 'aishimaj'


class TestGetEpnAndSplit(unittest.TestCase):
    def test1(self):
        dirname = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(get_epn(dirname), "10123g")

    def test2(self):
        dirname = "/data/MX1cal20150115k/frames/calibration/test_crystal/testcrystal_1_180.img"
        self.assertEqual(get_epn(dirname), "MX1cal20150115k")

if __name__ == '__main__':
    unittest.main()