__author__ = 'aishimaj'
import socket
from config import XDSME_COMMANDLINE
import copy
from processing.models import setup, Dataset, Collection
from beamline import variables as blconfig

def replace_top_directory_level(full_path, data_dir):
    """

    Replace the part of a path before EPN with what is in data_dir
    :param full_path:
    :param data_dir:
    :return: path with the part before EPN replaced by data_dir

    """
    import re
    import os

    if not data_dir.startswith(os.sep) or data_dir.endswith(os.sep):
        raise ValueError("data_dir must start with %s and not end with %s" % (os.sep, os.sep))

    use_full_path = False
    if full_path.startswith('/data/home'): # example: /data/home/10123g/aragaod...
        p=re.compile('^/data/home')
        dirsplit = re.split(p, full_path, 1)
        matched = p.search(full_path)
        last_part=dirsplit[1].split(os.sep)
        full_path = os.path.join(*last_part)
        use_full_path = True
    elif full_path.startswith('/data'): # example: /data/10123g/frames/...
        p=re.compile('^/data')
        dirsplit = re.split(p, full_path, 1)
        matched = p.search(full_path)
        last_part=dirsplit[1].split(os.sep)
        combined = os.path.join(data_dir, *last_part)
        return combined

    found_epn, dirsplit = get_epn_and_split(full_path)
    last_part=dirsplit[1].split(os.sep)
    if use_full_path:
        combined = os.path.join(data_dir, found_epn, "home", *last_part)
    else:
        combined= os.path.join(data_dir,found_epn, *last_part)
    return combined

def create_auto_dir_from_last_frame(last_frame):
    # general structure of last_frame is /data/$EPN/home/PI. We must add auto after the PI
    found_epn, dirsplit = get_epn_and_split(last_frame)
    import os
    last_part = dirsplit[1].split(os.sep)
    if last_part[1] == "frames":
        combined = os.path.join(dirsplit[0], found_epn, "home", last_part[2], "auto")
    else: # /data/home/EPN/...
        dirfront = dirsplit[0].split(os.sep)
        to_combine = os.path.join(os.sep, *dirfront[1:-2]), found_epn, "home", last_part[1], "auto"
        combined = os.path.join(*to_combine)
    return combined

def get_epn_and_split(last_frame):
    import re
    p=re.compile('MX[12]cal2[0-9]{7}[a-z]{0,}') #regex for MX cal visits
    p2=re.compile('[1-9][0-9]{2,5}[a-z]{0,}[0-9]{0,}(?!ays)') #regex for EPN - a bunch of numbers plus up to one letter

    psearch = p.search(last_frame)
    p2search = p2.search(last_frame)
    if psearch or p2search:
        if psearch: #MX cal done first since regular EPN is a subset of it
            successful_search = p
        else:
            successful_search = p2
        found_epn = re.findall(successful_search, last_frame)[0]
        dirsplit = re.split(successful_search, last_frame, 1)
        return found_epn, dirsplit

def get_epn(last_frame):
    return get_epn_and_split(last_frame)[0]

def get_valid_filenames(start, end, path, prefix, ext, detector_name, filename):
    if detector_name == 'eiger':
        return [filename]
    elif detector_name == 'adsc':
        pass
    else:
        raise Exception('Unknown detector type')
    import os
    import glob
    filenames = []
    for filenum in xrange(start, end+1):
        spec = os.path.join(path, "%s*%03d*%s" % (prefix, filenum, ext))
        filename = glob.glob(spec)
        if filename:
            filenames.append(filename[0])
    return filenames

def get_detector_specific_filename(filename, detector_name):
    if detector_name == 'adsc':
        return filename
    elif detector_name == 'eiger':
        master = '_master'
        return master.join(filename.split(master)[:-1])
    raise Exception('Unknown detector type')

def get_xdsme_commandline(hostname):
    try:
        return copy.deepcopy(XDSME_COMMANDLINE[hostname])
    except KeyError:
        return copy.deepcopy(XDSME_COMMANDLINE['default'])

class DryRunDataset(object):
    def __init__(self, _id=None):
        self._id = _id
        self.type = u'dataset'
        self.last_frame = ''
    def save(self):
        pass
    def reload(self):
        pass
    @classmethod
    def create_from_collection(cls, collection_id):
        a = cls()
        a.collection_id = collection_id
        return a

def get_retrigger_dir(dataset_id):
    setup(blconfig.get_database())
    dataset = Dataset(dataset_id)
    collection_id = dataset.collection_id.id
    PI = Collection(collection_id).PI
    return "/data/%(EPN)s/home/%(PI)s/auto" % {"EPN": blconfig.EPN, "PI": PI}
