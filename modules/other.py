__author__ = 'aishimaj'

from ccp4 import Process
from subprocess import call
from base import ReturnOptions
import h5py
import logging
from beamline import variables as blconfig
from beamline import oscillation

class Autorickshaw(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Autorickshaw, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        super(Autorickshaw, self).process(**kwargs)

        args = ['python2.7', '/xray/progs/Python/libraries/mx_auto_dataset/autorick_parse.py']

        call(args, cwd=self.project_dir)

class AutoStrategy(Process):
#Not ideal yet as it gets info from the PVs on qeGUI intead of geting the data from
#The collection object on mongoDB. Could create racing condition but good enough as a start. 
    def __init__(self, run_name, *args, **kwargs):
        super(AutoStrategy, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        super(AutoStrategy, self).process(**kwargs)

        try:
            if abs(float(oscillation.STRAT_RUN_AUTO) - 1.0) < 0.01:
                print 'using strategy to populate dataset'
                args = ['python2.7', '/xray/software/Python/applications/qeguitools/get_strategy_populate_collect.py']

                call(args, cwd=self.project_dir)
            else:
                print 'not pushing any strategy to dataset'
        except AttributeError:
            print 'No STRAT_RUN_AUTO PV available, skipping pushing of strategy'

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

def parse_adsc_header(filename):
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

def fix_beam_center(inputmap):
    fixmap = {'BEAM_CENTER_X_PIX': 'BEAM_CENTER_X', 'BEAM_CENTER_Y_PIX' : 'BEAM_CENTER_Y'}
    for (pix, mm) in  fixmap.items():
        inputmap[mm] = inputmap[pix] * inputmap['PIXEL_SIZE']
        del inputmap[pix]
    return inputmap

def fix_values(inputmap): # factor to multiply the current value by to get the correct value
    fixmap = {'BEAM_CENTER_X': 1000, 'BEAM_CENTER_Y': 1000, 'DISTANCE' : 1000, 'PIXEL_SIZE' : 1000}
    for (key, value) in fixmap.items():
        inputmap[key] = inputmap[key] * value
    return inputmap

def extract_eiger_header(filename):
    h5dbase = '/entry/instrument/detector/'
    h5map = {'BEAM_CENTER_X_PIX': h5dbase + 'beam_center_x', 'BEAM_CENTER_Y_PIX': h5dbase + 'beam_center_y',
     'SIZE1':         h5dbase + 'detectorSpecific/x_pixels_in_detector', 'SIZE2' : h5dbase + 'detectorSpecific/y_pixels_in_detector',
     'PIXEL_SIZE':    h5dbase + 'x_pixel_size',
     'DISTANCE':      h5dbase + 'detector_distance',
     'WAVELENGTH':    '/entry/instrument/beam/incident_wavelength'}

    f = h5py.File(filename)
    returnmap = {}
    for (key, value) in h5map.items():
        logging.debug(key, value)
        returnmap[key] = f.get(value)[()]
    returnmap = fix_beam_center(returnmap)
    returnmap = fix_values(returnmap)
    return returnmap

class CornerResolution(ReturnOptions):
    def __init__(self, run_name, *args, **kwargs):
        super(CornerResolution, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        if blconfig.detector_type == 'adsc':
            headermap = parse_adsc_header(self.dataset.last_frame)
        elif blconfig.detector_type == 'eiger':
            headermap = extract_eiger_header(self.dataset.last_frame)
        else:
            raise Exception('CornerResolution invalid detector type')
        res = Resolution()
        res.set_from_header(headermap)
        if not kwargs.get('high_resolution'):
            print "setting corner resolution", res.get_resolution()
            kwargs['high_resolution'] = str(res.get_resolution())
        else:
            print "keeping previously set resolution", kwargs.get('high_resolution')
        return kwargs
