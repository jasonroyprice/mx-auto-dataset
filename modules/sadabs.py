import os
import shutil
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
        super(Xprep, self).__init__()
        self.run_name = run_name
        self.filename = kwargs.get('filename')
        self.suffix = kwargs.get('suffix')

    def process(self, **kwargs):
        super(Xprep, self).process(**kwargs)
        args = ['xprep']
        import uuid
        use_shortened_name = False
        if len(self.filename)> 16: # if the name is too long for XPREP, such as XDS_ASCII.HKL_p1_noscale, then use a randomly generated short one
            self.original_filename = self.filename
            self.prefix = 'XDS_ASCII_%s' % str(uuid.uuid4())[0:4]
            self.filename = '%s.%s' % (self.prefix, 'HKL')
            use_shortened_name = True
            os.symlink('%s%s%s' % (self.project_dir, os.sep, self.original_filename), '%s%s%s' % (self.project_dir, os.sep, self.filename))
        if self.filename.startswith('XDS_ASCII'):
            stdin = [self.filename, os.linesep * 14, 'q']
        else:
            with open('%s%s%s' % (self.project_dir, os.sep, 'XDS_ASCII.HKL_p1_noscale')) as f:
                (unitcell, spacegroup) = uc_summary(f)
                unitcell = ' '.join(unitcell)
            stdin = [self.filename, os.linesep, '%s' % unitcell, os.linesep * 12, 'q']
        if not self.suffix:
            if os.path.exists('XDS_ASCII.prp'):
                raise Exception('xprep output file already exists, aborting')
        self.run_process(stdin, args, project_dir = self.project_dir, timeout = 10)
        if use_shortened_name:
            shutil.move('%s%s%s.prp' % (self.project_dir, os.sep, self.prefix), '%s%s%s.prp' % (self.project_dir, os.sep, os.path.splitext(self.original_filename)[0]))
            os.remove('%s%s%s' % (self.project_dir, os.sep, self.filename))
        if self.suffix and self.filename.startswith('XDS_ASCII'):
            shutil.move('%s%sXDS_ASCII.prp' % (self.project_dir, os.sep), '%s%sXDS_ASCII_%s.prp' % (self.project_dir, os.sep, self.suffix))

def find_header(file): # modeled on find_summary in custom_parser.py # also in merger/check_reindex.py - TODO consolidate these
    for line in file:
        if 'Header lines:' in line:
            break
    for line in file:
        if '!END_OF_HEADER' in line:
            break
        yield line

def uc_summary(lines):
    UNIT_CELL_STRING = '!UNIT_CELL_CONSTANTS='
    SPACE_GROUP_STRING = '!SPACE_GROUP_NUMBER='
    uc = None
    sg = None
    for line in lines:
        if line.startswith(UNIT_CELL_STRING):
            uc = line.split(UNIT_CELL_STRING)[1].split()
        if line.startswith(SPACE_GROUP_STRING):
            sg = line.split(SPACE_GROUP_STRING)[1].split()
    return (uc, sg)

class XprepSummary(Base):

    def __init__(self, *args, **kwargs):
        super(XprepSummary, self).__init__()
        self.run_name = 'XprepSummary'

    def process(self, **kwargs):
        create_rint_log(self.project_dir)

def create_rint_log(project_dir):
    with open('%s%srint_log.txt' % (project_dir, os.sep), 'w') as log:
        log.write('Resolution  #Data #Theory %Complete Redundancy Mean I Mean I/s R(int) Rsigma' + os.linesep)
        filenames = get_prp_filenames(project_dir)
        for filename in filenames:
            inflines = get_lines_with_text(filename, 'Inf')
            if len(inflines) > 0:
                log.write('%s %s%s' % (inflines[-1].strip(), filename.replace(project_dir, '')[1:], os.linesep))

def get_lines_with_text(filename, text):
    with open(filename) as f:
        textlines = []
        lines = f.readlines()
	for line in lines:
            if text in line:
                textlines.append(line)
    return textlines
def get_prp_filenames(project_dir):
    prp_filenames = []
    for root, subdir, files in os.walk(project_dir):
        for filename in files:
            if filename.endswith('.prp'):
                prp_filenames.append(os.path.join(root, filename))
    return prp_filenames
