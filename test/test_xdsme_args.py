import unittest
from config import XDSME_COMMANDLINE
import os
from utils import get_xdsme_commandline

class TestXdsmeCommandlineFromHostname(unittest.TestCase):
    def test_xdsme_commandline_with_defined_hostname(self):
        hostname = 'mxprocessing-test'
        self.assertEqual(XDSME_COMMANDLINE[hostname], ['xdsme', '-i', 'LIB=/usr/local/lib/dectris-neggia.so', '-n', '50'])

    def test_xdsme_commandline_with_set_hostname(self):
        os.environ['HOSTNAME'] = 'SR03ID01EPU02'
        self.assertEqual(get_xdsme_commandline(), ['xdsme', '--eiger', '-n', '50'])

    def test_xdsme_commandline_with_set_long_hostname(self):
        os.environ['HOSTNAME'] = 'SR03ID01EPU02.mx2.beamline.synchrotron.org.au'
        self.assertEqual(get_xdsme_commandline(), ['xdsme', '--eiger', '-n', '50'])

if __name__ == '__main__':
    unittest.main()
