from utils import get_detector_specific_filename
import unittest


class TestGetDetectorSpecificFilename(unittest.TestCase):
    def test1(self):
        filename = "testcrystal_1_180"
        detector_name = 'adsc'
        self.assertEqual(get_detector_specific_filename(filename, detector_name), "testcrystal_1_180")

    def test2(self):
        filename = "testcrystal_1_180_master"
        detector_name = 'eiger'
        self.assertEqual(get_detector_specific_filename(filename, detector_name), "testcrystal_1_180")

    def test3(self):
        filename = "testcrystal_master_1_180_master"
        detector_name = 'eiger'
        self.assertEqual(get_detector_specific_filename(filename, detector_name), "testcrystal_master_1_180")
