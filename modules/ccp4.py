from .base import Base
import subprocess
import os
import sys
from threading import Timer
from beamline import variables as blconfig

from custom_parser import get_summary

from aimless_rcp_batch import plot

class Process(Base):
    def process(self, **kwargs):
        super(Process, self).process(**kwargs)

        if not kwargs.get('no_harvest'):
            self.dataset.status = self.__class__.__name__
            self.dataset.save()

    def __write_logfile(self, process, output):
        logfile = os.path.join(self.project_dir, "%s.log" % process)
        with open(logfile, 'w') as f:
            f.write(output)


    def check_fatal_errors(self, output):
        if isinstance(output, list):
            line = output.next()
            try:
                while line:
                    if line.startswith('FATAL ERROR'):
                        raise Exception(output.next())
                    line = output.next()
            except StopIteration:
                pass  # expected end for a clean file


    def run_process(self, input_, args, **kwargs):
        process_project_dir = self.project_dir
        project_dir = kwargs.get('project_dir')
        if project_dir:
            process_project_dir = project_dir
        timeout = kwargs.get('timeout')
        process = subprocess.Popen(args,
                                   stderr=subprocess.STDOUT,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    cwd=process_project_dir)
        t = Timer(timeout, process.kill)
        try:
            t.start()
            out, err = process.communicate(input='\n'.join(input_))
        finally:
            t.cancel()

        self.__write_logfile(args[0], out)
        self.check_fatal_errors(out)


class Pointless(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Pointless, self).__init__()
        self.run_name = run_name
        if kwargs.get('project_dir'):
            self.project_dir = kwargs.get('project_dir')
        if kwargs.get('nonchiral') == True:
            self.stdin = ['chirality nonchiral']
        else:
            self.stdin = []

    def process(self, **kwargs):
        super(Pointless, self).process(**kwargs)
        
        #xdsin = os.path.basename(getattr(self, 'xds_%s' % self.run_name))
        input_filename = kwargs.get('input_filename')
        if input_filename:
            xdsin = input_filename
        else:
            xdsin = 'XDS_ASCII.HKL_%s' % self.run_name
        hklout = 'pointless_%s.mtz' % self.run_name

        args = ['pointless', '-copy', 'XDSIN', xdsin, 'HKLOUT', hklout]
        self.run_process(self.stdin, args)
        
class Aimless(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Aimless, self).__init__()
        self.run_name = run_name
        if kwargs.get('project_dir'):
            self.project_dir = kwargs.get('project_dir')

    def process(self, **kwargs):
        super(Aimless, self).process(**kwargs)
        
        hklin = 'pointless_%s.mtz' % self.run_name
        hklout = 'aimless_%s.mtz' % self.run_name

        args = ['aimless', 'HKLIN', hklin, 'HKLOUT', hklout]
        if kwargs.get('constant_scales') == True:
            stdin =  ["run 1 all",
                      "scales constant",
                    "cycles 20",
                    "anomalous on",
                     "sdcorrection 1.3 0.02",
                     "reject 4", ""]
        else:
            stdin = ["run 1 all",
                "cycles 20",
                "anomalous on",
                "sdcorrection 1.3 0.02",
                "reject 4", ""]
        self.run_process(stdin, args)
        if not kwargs.get('no_harvest'):
            self.harvest()

    def harvest(self):
        logfile = os.path.join(self.project_dir, 'aimless.log')
        summary = get_summary(logfile)

        space_group = ''.join(summary['space_group'])
        unit_cell=summary['average_unit_cell']
        average_mosaicity=summary['average_mosaicity'][0]
        del summary['space_group'], summary['average_unit_cell'], summary['average_mosaicity']

        self.dataset.__dict__.update(space_group=space_group,
                     resolution=summary['high_resolution_limit'][0],
                     unit_cell=unit_cell,
                     average_mosaicity=average_mosaicity,
                     #status='Success',
                     #success=True,
                     #completed=True,
                     #processing_dir=self.project_dir,
                     **summary)
        self.dataset.save()        

class AimlessPlot(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(AimlessPlot, self).__init__()
        self.run_name = run_name
    def process(self, **kwargs):
        keyname = '%s:%s:%s:rmerge_plot' % (self.dataset.beamline, self.dataset.epn, self.project_dir.replace('/','_'))
        try:
            plot(directory=self.project_dir, write_to_redis=True, redis_key=keyname)
            self.dataset.__dict__.update(rmerge_plot=keyname)
            self.dataset.save()
        except:
            print 'exception during Rcp plot generation: type: %s value: %s traceback: %s' % sys.exc_info()

class AimlessScalePlot(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(AimlessScalePlot, self).__init__()
        self.run_name = run_name
    def process(self, **kwargs):
        keyname = '%s:%s:%s:scale_plot' % (self.dataset.beamline, self.dataset.epn, self.project_dir.replace('/','_'))
        try:
            plot_scale(directory=self.project_dir, write_to_redis=True, redis_key=keyname)
            self.dataset.__dict__.update(scale_plot=keyname)
            self.dataset.save()
        except:
            print 'exception during scale plot generation: type: %s value: %s traceback: %s' % sys.exc_info()

class Truncate(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Truncate, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        super(Truncate, self).process(**kwargs)
        
        hklin = 'aimless_%s.mtz' % self.run_name
        hklout = 'truncate_%s.mtz' % self.run_name

        args =  ['truncate', 'HKLIN', hklin, 'HKLOUT', hklout]
        stdin = ["anomalous yes",
                "nresidue 1049",
                "labout  F=FP SIGF=SIGFP DANO=DANO_sulf SIGDANO=SIGDANO_sulf", ""]

        self.run_process(stdin, args)
