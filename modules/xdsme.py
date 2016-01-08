from .base import Base
from subprocess import call, check_output
import os
import shutil

class XDSme(Base):
    XDS_INPUT = ['SENSOR_THICKNESS= 0.01']

    def __init__(self, run_name, *args, **kwargs):
        super(XDSme, self).__init__()
        self.run_name = run_name
        self.args = args
        self.kwargs = kwargs
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

    def process(self, first_frame, last_frame,
                low_resolution, high_resolution,
                ice, weak, slow, brute,
                unit_cell, space_group,
                **kwargs):
        self.dataset.status = "XDS %s" % self.run_name
        self.dataset.save()

        extra = []

        if first_frame:
            extra.extend(['-F', first_frame])
        if last_frame:
            extra.extend(['-L', last_frame])

        if low_resolution:
            extra.extend(['-R', low_resolution])
        if high_resolution:
            extra.extend(['-r', high_resolution])

        if unit_cell:
            extra.extend(['-c', unit_cell])
        if space_group:
            extra.extend(['-s', space_group])

        if ice:
            extra.extend(['--ice'])
        if weak:
            extra.extend(['--weak'])
        if slow:
            extra.extend(['--slow'])
        if brute:
            extra.extend(['--brute'])

        self.run_xdsme(extra)
        self.move_files()

    def run_xdsme(self, extra):
        args = ['xdsme']
        args.extend(['-p', self.output.project])
        args.extend(['-i', ' '.join(self.XDS_INPUT)])
        if self.p1:
            sg, cell = self.__get_cell_and_sg()
            args.extend(['-s', sg])
            args.extend(['-c', cell])
        args.extend(self.args)
        args.extend(extra)
        args.extend(self.output.images)

        call(args, cwd=self.base_dir)

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
        with open(os.path.join(self.project_dir, 'INTEGRATE.HKL')) as f:
            for line in f:
                if 'SPACE_GROUP_NUMBER' in line:
                    sg = line.split('=')[1].strip()
                if 'UNIT_CELL_CONSTANTS' in line:
                    cell = ' '.join(line.split('=')[1].split())
        return sg, cell
