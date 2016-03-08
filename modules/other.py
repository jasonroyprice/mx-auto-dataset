__author__ = 'aishimaj'

from ccp4 import Process
from subprocess import call
from base import ReturnOptions

class Autorickshaw(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Autorickshaw, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        super(Autorickshaw, self).process(**kwargs)

        args = ['python2.7', '/xray/progs/Python/libraries/mx_auto_dataset/autorick_parse.py']

        call(args, cwd=self.project_dir)

class Resolution(object):
    def __init__(self):
        pass
    def set_from_header(self, headermap):
        self.beam_center_x = float(headermap['BEAM_CENTER_X']) #mm
        self.beam_center_y = float(headermap['BEAM_CENTER_Y']) #mm
        self.size1 = int(headermap['SIZE1']) #pixels x
        self.size2 = int(headermap['SIZE2']) #pixels y
        self.pixel_size = float(headermap['PIXEL_SIZE']) #mm
        self.distance = float(headermap['DISTANCE']) #mm
        self.wavelength = float(headermap['WAVELENGTH']) #angstrom
    def get_resolution(self):
        max_distance_x = max(self.beam_center_x / self.pixel_size, self.size1 - self.beam_center_x / self.pixel_size)
        max_distance_y = max(self.beam_center_y / self.pixel_size, self.size2 - self.beam_center_y / self.pixel_size)
        import math
        res = 0.5/math.sin(math.atan2(((max_distance_x*self.pixel_size)**2 + (max_distance_y*self.pixel_size)**2)**0.5,self.distance)/2) * self.wavelength
        return res
    def get_edge_resolution(self):
        min_distance = min(self.beam_center_y / self.pixel_size, self.size2 - self.beam_center_y / self.pixel_size, self.beam_center_x / self.pixel_size, self.size1 - self.beam_center_y / self.pixel_size) #note this is closest minimum distance
        min_distance = max(self.beam_center_y / self.pixel_size, self.size2 - self.beam_center_y / self.pixel_size, self.beam_center_x / self.pixel_size, self.size1 - self.beam_center_y / self.pixel_size) #note this is furthest edge distance
        import math
        res = 0.5/math.sin(math.atan2(min_distance*self.pixel_size,self.distance)/2) * self.wavelength
        return res

class CornerResolution(ReturnOptions):
    def __init__(self, run_name, *args, **kwargs):
        super(CornerResolution, self).__init__()
        self.run_name = run_name

    def parse_adsc_header(self, filename):
        import re
        header_map = {}
        with open(filename, 'r') as f:
            line = f.readline()
            assert(line.strip()== "{")
            line = f.readline()
            while "}" not in line:
                sp = filter(None, re.split("[;= ]", line.strip()))
                header_map[sp[0]] = sp[1]
                line = f.readline()
        return header_map

    def process(self, **kwargs):
        headermap = self.parse_adsc_header(self.dataset.last_frame)
        res = Resolution()
        res.set_from_header(headermap)
        kwargs['high_resolution'] = str(res.get_resolution())
        return kwargs