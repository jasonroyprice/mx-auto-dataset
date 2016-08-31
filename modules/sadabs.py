import os
from .ccp4 import Process
from .base import Base
from subprocess import call

class Xds2sad(Base):

    def __init__(self, run_name, *args, **kwargs):
        super(Xds2sad, self).__init__()
        self.run_name = run_name
        self.filename = kwargs.get('filename')

    def process(self, **kwargs):
        if self.filename:
            args = ['xds2sad', self.filename]
        else:
            args = ['xds2sad'] # assume we're using XDS_ASCII.HKL
        call(args, cwd=self.project_dir)
        
class Sadabs(Process):
    ABSORBANCE = {'weak':'w', 'moderate':'m', 'strong':'s'}

    def __init__(self, run_name, *args, **kwargs):
        super(Sadabs, self).__init__()
        self.run_name = run_name
        absorber_strength = kwargs.get('absorber_strength')
        if absorber_strength and absorber_strength in self.ABSORBANCE:
            self.absorber = self.ABSORBANCE[absorber_strength]
        else:
            raise Exception('No valid absorber type specified')

    def process(self, **kwargs):
        super(Sadabs, self).process(**kwargs)
        dir_name = '%s%ssadabs_%s' % (self.project_dir, os.sep, self.absorber)
        os.mkdir(dir_name)
        os.symlink('%s%sxds.sad' % (self.project_dir, os.sep), '%s%sxds.sad' % (dir_name, os.sep))

        args = ['sadabs']

        stdin = [os.linesep, '1', 'xds.sad', os.linesep * 4, self.absorber, os.linesep * 10]

        self.run_process(stdin, args, project_dir = dir_name)

class Xprep(Process):

    def __init__(self, run_name, *args, **kwargs):
        pass

    def process(self, **kwargs):
        pass
