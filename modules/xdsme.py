from .base import Base
from subprocess import call, check_output, CalledProcessError, STDOUT
import os
import shutil
from beamline import redis as BLredis
from utils import get_xdsme_commandline
import json
import socket
from beamline import variables as mxvars

class Trigger(dict):
    pass

class XDSme(Base):
    XDS_INPUT = []

    def __init__(self, run_name, display_name, *args, **kwargs):
        super(XDSme, self).__init__()
        self.run_name = run_name
        self.display_name = display_name
        self.args = args
        self.kwargs = kwargs
        self.subtype = kwargs.get('subtype')
        self.p1 = kwargs.get('p1', False)

    def __repr__(self):
        return 'XDSme(%s)' % self.display_name

    @staticmethod
    def add_args(parser):
        parser.add_argument('--first_frame')
        parser.add_argument('--last_frame')
        parser.add_argument('--low_resolution')
        parser.add_argument('--high_resolution')
        parser.add_argument('--ice')
        parser.add_argument('--weak')
        parser.add_argument('--slow')
        parser.add_argument('--brute')
        parser.add_argument('--unit_cell')
        parser.add_argument('--space_group')
        parser.add_argument('--from_start')

    def process(self, first_frame, last_frame,
                low_resolution, high_resolution,
                ice, weak, slow, brute,
                unit_cell, space_group,
                from_start,
                **kwargs):
        self.dataset.status = "XDS %s" % self.display_name
        if self.subtype is not None:
            self.dataset.subtype = self.subtype
        self.dataset.save()

        extra = []

        retrigger = Trigger()
        if first_frame:
            extra.extend(['-F', first_frame])
            retrigger['first_frame'] = int(first_frame)
        if last_frame:
            extra.extend(['-L', last_frame])
            retrigger['last_frame'] = int(last_frame)

        if low_resolution:
            extra.extend(['-R', low_resolution])
            retrigger['low_resolution'] = float(low_resolution)
        if high_resolution:
            extra.extend(['-r', high_resolution])
            retrigger['high_resolution'] = float(high_resolution)

        if not self.p1:
            if unit_cell:
                parms = unit_cell[1:-1].split(',')
                cell = ''
                for parm in parms:
                    cell += parm.strip() + " "
                extra.extend(['-c', cell])
            if space_group:
                extra.extend(['-s', space_group])

        if unit_cell:
            retrigger['unit_cell'] = unit_cell
        if space_group:
            retrigger['space_group'] = space_group

        if ice:
            extra.extend(['--ice'])
            retrigger['ice'] = True
        if weak:
            extra.extend(['--weak'])
            retrigger['weak'] = True
        if slow:
            extra.extend(['--slow'])
            retrigger['slow'] = True
        if brute:
            extra.extend(['--brute'])
            retrigger['brute'] = True
        if from_start:
            retrigger['from_start'] = True

        if retrigger:
            self.dataset.retrigger = retrigger
            self.dataset.save()

        self.run_xdsme(extra)
        self.move_files()

    def run_xdsme(self, extra):
        hostname = socket.gethostname().split('.')[0]
        args = get_xdsme_commandline(hostname)
        if int(BLredis.get('SMX')) == 1:
            args.extend(['--index_refine'])
        args.extend(['-p', self.output.project])
        if self.XDS_INPUT:
            args.extend(['-i', ' '.join(self.XDS_INPUT)])
        if self.p1:
            sg, cell = self.__get_cell_and_sg()
            args.extend(['-s', sg])
            args.extend(['-c', cell])
        args.extend(self.args)
        args.extend(extra)
        args.extend(self.output.images)

        if args[0] in ['xdsme', 'nice']:
            call(args, cwd=self.base_dir)
        else:
            labels=dict(
                  epn=mxvars.EPN,
                  project=self.output.project,
                  xds="master")
            try:
                jib_request = dict(labels=labels, working_dir=self.base_dir, hostname=hostname.lower())
                call(args, stderr=STDOUT, env={"JIB_REQUEST":json.dumps(jib_request)})
            except CalledProcessError as e:
                print 'call error output and returncode', e.output, e.returncode

    def move_files(self, ):
        correct = os.path.join(self.project_dir, 'CORRECT.LP')
        correct_target = os.path.join(self.project_dir, "%s_%s" % (correct, self.run_name))

        hkl = os.path.join(self.project_dir, 'XDS_ASCII.HKL')
        hkl_target = os.path.join(self.project_dir, "%s_%s" % (hkl, self.run_name))

        os.rename(correct, correct_target)
        os.rename(hkl, hkl_target)

        output_dir = os.path.join(self.project_dir, 'output')
        try:
            os.makedirs(output_dir)
        except EnvironmentError:
            pass

        shutil.copy(correct_target, output_dir)
        shutil.copy(hkl_target, output_dir)

        setattr(self.output, 'xds_%s' % self.run_name, hkl_target)


    def __get_cell_and_sg(self):
        with open(os.path.join(self.project_dir, 'IDXREF.LP')) as f:
            numbersgstring = 0 #look for second SPACE GROUP NUMBER before parsing

            sgstring = 'SPACE GROUP NUMBER'
            ucstring = 'UNIT CELL PARAMETERS'

            for line in f:
                if sgstring in line:
                    numbersgstring += 1
                if numbersgstring == 2:
                    if sgstring in line:
                        sg = line.split(sgstring)[1].split()[0]
                    if ucstring in line:
                        cell = ' '.join(line.split(ucstring)[1].split())
        return sg, cell
