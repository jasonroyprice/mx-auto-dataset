import unittest
from config import XDSME_COMMANDLINE
import os
from utils import get_xdsme_commandline

class TestXdsmeCommandlineFromHostname(unittest.TestCase):
    def test_xdsme_commandline_with_defined_hostname(self):
        hostname = 'mxprocessing-test'
        self.assertEqual(XDSME_COMMANDLINE[hostname], ['xdsme', '-i', 'LIB=/usr/local/lib/dectris-neggia.so', '-n', '50'])

    def test_xdsme_commandline_with_set_hostname(self):
        self.assertEqual(get_xdsme_commandline('SR03ID01EPU02'), ['xdsme', '--eiger', '--library', '/usr/local/lib/dectris-neggia.so', '-n', '50'])

    def test_xdsme_commandline_with_cluster_hostname(self):
        cluster_hostname = 'SR03ID01DAT01'
        self.assertEqual(get_xdsme_commandline(cluster_hostname), ['vkube_xdsme.sh', 'xdsme'])

if __name__ == '__main__':
    unittest.main()
