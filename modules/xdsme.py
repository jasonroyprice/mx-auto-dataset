from .base import Base
from subprocess import call, check_output, CalledProcessError, STDOUT, PIPE, Popen
import os
import shutil
from beamline import redis as BLredis
from utils import get_xdsme_commandline
import json
import socket
from beamline import variables as mxvars
from processing.models import Collection

def parse_strategies(stdout_buffer):
    strategies_map = {}
    strategies = []
    sg_num = ''
    uc = None
    while 1:
        line = stdout_buffer.readline()
        if not line:
            break
        print line.rstrip()
        if 'Assuming that the currently processed data satisfy' in line:
            for i in range(0,2):
                line = stdout_buffer.readline()
                print line
            linesplit = line.split() # SPACE_GROUP_NUMBER
            sg_num = linesplit[1]
            line = stdout_buffer.readline()
            print line
            linesplit = line.split() # UNIT_CELL_CONSTANTS
            uc = linesplit[1:]
        if 'starting at     total rotation     completeness        multiplicity of' in line:
            for i in range(0,3):
                line = stdout_buffer.readline()
            linesplit = line.split()
            print line.rstrip()
            while len(linesplit):
                strategies.append({'multiplicity':linesplit[3], 'start_angle': linesplit[0], 'wedge': linesplit[1], 'completeness': linesplit[2]})
                line = stdout_buffer.readline()
                print line.rstrip()
                linesplit = line.split()

    if not uc:
        raise Exception('No unit cell information available')
    strategies_map['input'] = '%s:%s' % (sg_num, ':'.join(uc))
    strategies_map['strategies'] = strategies
    return strategies_map

class Trigger(dict):
    pass

class XDSme(Base):
    XDS_INPUT = []

    def __init__(self, run_name, *args, **kwargs):
        super(XDSme, self).__init__()
        self.run_name = run_name
        self.args = args
        self.kwargs = kwargs
        self.subtype = kwargs.get('subtype')
        self.p1 = kwargs.get('p1', False)

    def __repr__(self):
        return 'XDSme(%s)' % self.run_name

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
        parser.add_argument('--strategy')
        parser.add_argument('--skip_defpix', action='store_true')
        parser.add_argument('--minimum_total_spindle_angle', default='30')
        parser.add_argument('--maximum_total_spindle_angle', default='360')
        parser.add_argument('--increment_total_spindle_angle', default='30')
        parser.add_argument('--minimum_start_spindle_angle')
        parser.add_argument('--maximum_start_spindle_angle')
        parser.add_argument('--increment_start_spindle_angle')

    def process(self, first_frame, last_frame,
                low_resolution, high_resolution,
                ice, weak, slow, brute,
                unit_cell, space_group,
                from_start,strategy,skip_defpix,
                minimum_total_spindle_angle, maximum_total_spindle_angle, increment_total_spindle_angle,
                minimum_start_spindle_angle, maximum_start_spindle_angle, increment_start_spindle_angle,
                **kwargs):
        self.dataset.status = "XDS %s" % self.run_name
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
        self.strategy = False
        if strategy:
            self.strategy = True
        if skip_defpix:
            extra.extend(['--skip_defpix'])

        if minimum_total_spindle_angle:
            extra.extend(['--minimum_total_spindle_angle', minimum_total_spindle_angle])
        if maximum_total_spindle_angle:
            extra.extend(['--maximum_total_spindle_angle', maximum_total_spindle_angle])
        if increment_total_spindle_angle:
            extra.extend(['--increment_total_spindle_angle', increment_total_spindle_angle])
        if minimum_start_spindle_angle:
            extra.extend(['--minimum_start_spindle_angle', minimum_start_spindle_angle])
        if maximum_start_spindle_angle:
            extra.extend(['--maximum_start_spindle_angle', maximum_start_spindle_angle])
        if increment_start_spindle_angle:
            extra.extend(['--increment_start_spindle_angle', increment_start_spindle_angle])

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
        if self.strategy:
            args.extend(['-S'])
        args.extend(self.args)
        args.extend(extra)
        args.extend(self.output.images)

        if args[0] == 'xdsme':
            process = Popen(args, stdout=PIPE, stderr=STDOUT, cwd=self.base_dir)
            if '--strategy' in args or '-S' in args:
                strategies_map = parse_strategies(process.stdout)
                coll = Collection(self.dataset.collection_id.id)
                anom_key = 'noanom'
                if '-a' in args or '-A' in args:
                    anom_key = 'anom'
                strat_key = '%s:%s:strategies:%04d:%s:%s' % (coll.beamline, coll.EPN, int(coll.run_label), anom_key, strategies_map['input'])
                if mxvars.redis.get(strat_key):
                    print 'warning, strategy key %s will be changed' % (strat_key)
                ex = 60*60*24*30*3 # seconds in 3 months
                mxvars.redis.set(strat_key, json.dumps(strategies_map['strategies']), ex=ex) # TODO this really should be sample ID-based instead of run label
            else:
                # no strategies, so skipping searching for them
                out, err = process.communicate()
                print out, err
        else:
            labels=dict(
                  epn=mxvars.EPN,
                  project=self.output.project,
                  xds="master")

            try:
                jib_request = dict(labels=labels, working_dir=self.base_dir, hostname=hostname.lower())
                process = Popen(args, stdout=PIPE, stderr=STDOUT, env={"JIB_REQUEST":json.dumps(jib_request)}, cwd=self.base_dir)
                if '--strategy' in args or '-S' in args:
                    strategies_map = parse_strategies(process.stdout)
                    coll = Collection(self.dataset.collection_id.id)
                    anom_key = 'noanom'
                    if '-a' in args or '-A' in args:
                        anom_key = 'anom'
                    strat_key = '%s:%s:strategies:%04d:%s:%s' % (coll.beamline, coll.EPN, int(coll.run_label), anom_key,              strategies_map['input'])
                    if mxvars.redis.get(strat_key):
                         print 'warning, strategy key %s will be changed' % (strat_key)
                    ex = 60*60*24*30*3 # seconds in 3 months
                    mxvars.redis.set(strat_key, json.dumps(strategies_map['strategies']), ex=ex) # TODO this really should be         sample ID-based instead of run label
                else:
                    # no strategies, so skipping searching for them
                    out, err = process.communicate()
                    print out, err
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
