import unittest
from utils import get_valid_filenames

class TestGetValidFilenames(unittest.TestCase):
    def test1(self):
        start = 10
        end = 20
        path = "files"
        prefix = "testempty_1_"
        suffix = "img"
        filenames = get_valid_filenames(start, end, path, prefix, suffix)
        self.assertEquals(len(filenames), 8)