__author__ = 'aishimaj'

from ccp4 import Process
from subprocess import call

class Autorickshaw(Process):
    def __init__(self, run_name, *args, **kwargs):
        super(Autorickshaw, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        super(Autorickshaw, self).process(**kwargs)

        args = ['python2.7', '/xray/progs/Python/libraries/mx_auto_dataset/autorick_parse.py']

        call(args, cwd=self.project_dir)
