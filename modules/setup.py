import os
import glob
import shutil

from beamline import variables as blconfig

from .base import Base

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
        default_base_dir = os.path.join(blconfig.AUTO_DIR, 'dataset')
        self.output.base_dir = kwargs.get('base_dir', default_base_dir)
        self.output.project_dir = os.path.join(self.output.base_dir, 'xds_process_%s' % (self.output.project,))

        self.dataset.processing_dir = self.project_dir
        self.dataset.save()



class Retrigger(Base):
    def process(self, **kwargs):
        os.mkdir(self.project_dir)

        for item in ('INTEGRATE.HKL',
                     'FILTER.HKL',
                     'REMOVE.HKL',
                     'X-CORRECTIONS.cbf',
                     'Y-CORRECTIONS.cbf',
                     'XPARM.XDS'):
            src = os.path.join(self.from_dataset.processing_dir, item)
            dst = os.path.join(self.project_dir, item)
            
            if os.path.exists(src):
                os.symlink(src,dst)