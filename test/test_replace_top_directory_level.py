__author__ = 'aishimaj'

from utils import replace_top_directory_level

def test1():
    test_dir = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
    data_dir = "/sans/60days"
    result = replace_top_directory_level(test_dir, data_dir)
    assert result == "/sans/60days/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"

def test2():
    test_dir = "/data/10123g/frames/calibration/test_crystal/testcrystal_1_180.img"
    data_dir = "/sans/60days/"
    try:
        result = replace_top_directory_level(test_dir, data_dir)
    except ValueError, e:
        pass #this is the expected behavior
    raise Exception("failed")

test1()
test2()