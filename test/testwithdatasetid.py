import logbook
logger = logbook.Logger(__name__)

__author__ = 'aishimaj'
from beamline import get_database
from mx_auto_dataset.mx_auto_dataset import dataset
from processing.models import setup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_id", help="dataset ID")
parser.add_argument("--data_dir", help="top-level directory name (like /data for most data)")
parser.add_argument("--output_dir", help="place where processing results are put")
parser.add_argument('--unit_cell', default='', help="Format: '[a, b, c, al, be, ga]'")
parser.add_argument('--space_group', default='')
parser.add_argument('--first_frame', default='')
parser.add_argument('--last_frame', default='')
parser.add_argument('--low_resolution', default='')
parser.add_argument('--high_resolution', default='')
parser.add_argument('--ice', default='')
parser.add_argument('--weak', default='')
parser.add_argument('--slow', default='')
parser.add_argument('--brute', default='')
parser.add_argument('--staging', type=bool, default=False)

args = parser.parse_args()
setup(get_database(staging=args.staging))

if not args.dataset_id:
    import sys
    sys.exit("no dataset ID provided, aborting")
job = dataset.delay(dataset_id=unicode(args.dataset_id), data_dir=unicode(args.data_dir),
                    output_dir=unicode(args.output_dir), unit_cell=unicode(args.unit_cell),
                    space_group=unicode(args.space_group), first_frame=unicode(args.first_frame),
                    last_frame=unicode(args.last_frame), low_resolution=unicode(args.low_resolution),
                    high_resolution=unicode(args.high_resolution), weak=unicode(args.weak), slow=unicode(args.slow),
                    brute=unicode(args.brute), ice=unicode(args.ice))
logger.info('Queued dataset job with id = %s' % (job,))
