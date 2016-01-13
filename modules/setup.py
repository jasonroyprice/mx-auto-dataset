from idlelib.ReplaceDialog import replace
import os
import glob
import shutil

from beamline import variables as blconfig

from .base import Base

from utils import create_auto_dir_from_last_frame, replace_top_directory_level

#def folder_from_dataset(dataset):
#    _, filename = os.path.split(dataset.last_frame)
#    return "%s_%s" % (filename, dataset._id)

class Setup(Base):
    def process(self, **kwargs):
        self.dataset.status = 'Starting...'
        self.dataset.completed = False
        self.dataset.save()

        # get details from file
        path, filename = os.path.split(self.dataset.last_frame)
        filename, ext = os.path.splitext(filename)
        prefix, frame = filename.rsplit('_', 1)

        # get image list
        spec = os.path.join(path, "%s*%s" % (prefix, ext))

        # set image list and project
        self.output.images = sorted(glob.glob(spec))
        #self.output.project = "%s_%d" % (filename, os.stat(dataset.last_frame).st_ctime)
        self.output.project = "%s_%s" % (filename, self.dataset._id)

        # set project dir
        base_dir = blconfig.AUTO_DIR
        data_dir = kwargs.get('data_dir')
        output_dir = kwargs.get('output_dir')

        if data_dir and not output_dir:
            base_dir = create_auto_dir_from_last_frame(replace_top_directory_level(self.dataset.last_frame, data_dir))

        elif output_dir:
            base_dir = create_auto_dir_from_last_frame(replace_top_directory_level(self.dataset.last_frame, output_dir))

        default_base_dir = os.path.join(base_dir, 'dataset')
        self.output.base_dir = kwargs.get('base_dir', default_base_dir)
        self.output.project_dir = os.path.join(self.output.base_dir, 'xds_process_%s' % (self.output.project,))

        self.dataset.processing_dir = self.project_dir
        self.dataset.save()



class Retrigger(Base):
    def __init__(self, stepnumber = 5):
        super(Retrigger, self).__init__()
        self.stepnumber = stepnumber
    def file_lists(self, stepnumber):
        if stepnumber == 5:
            linkfiles = ['INTEGRATE.HKL',
                     'FILTER.HKL',
                     'REMOVE.HKL',
                     'X-CORRECTIONS.cbf',
                     'Y-CORRECTIONS.cbf']
            return linkfiles, ''
        elif stepnumber == 3:
            linkfiles = ['INTEGRATE.LP',
                     'INTEGRATE.HKL',
                     'X-CORRECTIONS.cbf',
                     'Y-CORRECTIONS.cbf',
                     'BKGINIT.cbf',
                     'GAIN.cbf']
            copyfiles = ['SPOT.XDS']
            return linkfiles, copyfiles
    def process(self, **kwargs):
        linkfiles, copyfiles = self.file_lists(self.stepnumber)
        os.makedirs(self.project_dir)

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