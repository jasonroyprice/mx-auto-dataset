import os
import glob
import shutil
import socket

from beamline import variables as blconfig

from .base import Base

from utils import create_auto_dir_from_last_frame, replace_top_directory_level, get_epn, get_valid_filenames, \
    get_detector_specific_filename

from processing.models import Collection

class Setup(Base):
    def __init__(self, suffix = '', *args, **kwargs):
        super(Setup, self).__init__()
        self.suffix = suffix
        self.detector_type = kwargs.get('detector', 'adsc')

    def process(self, **kwargs):
        self.dataset.status = 'Starting...'
        self.dataset.completed = False
        self.dataset.save()

        # get details from file
        path, filename = os.path.split(self.dataset.last_frame)
        filename, ext = os.path.splitext(filename)
        if self.detector_type == 'eiger':
            filename = filename.split('_master')[0]
        prefix, frame = filename.rsplit('_', 1)

        # get image list
        spec = os.path.join(path, "%s*%s" % (prefix, ext))

        # set image list and project
        collection = Collection(self.dataset.collection_id.id)
        self.output.images = get_valid_filenames(int(collection.start_frame),
                                                 int(collection.no_frames) + int(collection.start_frame), path, prefix,
                                                 ext, self.detector_type, self.dataset.last_frame)
        import time
        self.output.project = "%s_%s_%s" % (filename, time.strftime("%Y%m%d-%H%M%S"), self.suffix)

        # set project dir
        if get_epn(self.dataset.last_frame) == blconfig.EPN:
            base_dir = blconfig.AUTO_DIR
        else: # re-trigger back into previous EPN's directory if we're not looking at current data
            if hasattr(self.input, 'from_dataset'):
                base_dir = create_auto_dir_from_last_frame(self.input.from_dataset.last_frame)
            else:
                base_dir = create_auto_dir_from_last_frame(self.dataset.last_frame)
        data_dir = kwargs.get('data_dir')
        output_dir = kwargs.get('output_dir')

        if data_dir and not output_dir:
            base_dir = create_auto_dir_from_last_frame(replace_top_directory_level(self.dataset.last_frame, data_dir))

        elif output_dir:
            base_dir = create_auto_dir_from_last_frame(replace_top_directory_level(self.dataset.last_frame, output_dir))

        default_base_dir = os.path.join(base_dir, 'dataset')
        self.output.base_dir = kwargs.get('base_dir', default_base_dir)
        if not os.path.exists(self.output.base_dir):
            os.makedirs(self.output.base_dir)
        self.output.project_dir = os.path.join(self.output.base_dir, '%s' % (self.output.project,))

        if not os.path.exists(self.output.project_dir):
            os.makedirs(self.output.project_dir)
        with open(os.path.join(self.output.project_dir, 'processing_info.txt'), 'w') as setup_file:
            setup_file.write('HOSTNAME: %s' % socket.gethostname() + os.linesep)
            setup_file.write(str(kwargs) + os.linesep)

        self.dataset.processing_dir = self.project_dir
        self.dataset.save()



class Retrigger(Base):
    def __init__(self, stepnumber = 5):
        super(Retrigger, self).__init__()
        self.stepnumber = stepnumber
    def file_lists(self, stepnumber):
        if stepnumber == 5:
            linkfiles = ['IDXREF.LP',
                     'INTEGRATE.HKL',
                     'FILTER.HKL',
                     'REMOVE.HKL',
                     'X-CORRECTIONS.cbf',
                     'Y-CORRECTIONS.cbf',
                     'XPARM.XDS']
            return linkfiles, ''
        elif stepnumber == 3:
            linkfiles = ['INTEGRATE.LP',
                     'INTEGRATE.HKL',
                     'X-CORRECTIONS.cbf',
                     'Y-CORRECTIONS.cbf',
                     'BKGINIT.cbf',
                     'BLANK.cbf',
                     'GAIN.cbf']
            copyfiles = ['SPOT.XDS',
                     'XPARM.XDS']
            return linkfiles, copyfiles
    def process(self, **kwargs):
        linkfiles, copyfiles = self.file_lists(self.stepnumber)
        if not os.path.exists(self.project_dir):
            print 'retrigger: need to create directories, but should have been done by now!'
            os.makedirs(self.project_dir)
        else:
            print 'retrigger: do not need to create directories (expected)'

        # many files just need to be linked to the old directory - they are only read
        for item in (linkfiles):
            src = os.path.join(self.from_dataset.processing_dir, item)
            dst = os.path.join(self.project_dir, item)
            
            try:
                os.symlink(src,dst)
            except:
                print "warning, %s to %s symlink could not be made" % (src, dst)

        # some files may need to be copied because they are re-written
        import shutil
        for item in (copyfiles):
            shutil.copyfile(os.path.join(self.from_dataset.processing_dir, item), \
                os.path.join(self.project_dir, item))
