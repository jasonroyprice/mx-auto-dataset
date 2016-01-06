import logbook
logger = logbook.Logger(__name__)

__author__ = 'aishimaj'
from beamline import get_database
from mx_auto_dataset import dataset
from processing.models import setup
import argparse

setup(get_database(staging=True))

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_id", help="dataset ID")
parser.add_argument("--data_dir", help="top-level directory name (like /data for most data)")
args = parser.parse_args()
if not args.dataset_id:
    import sys
    sys.exit("no dataset ID provided, aborting")
job = dataset.delay(dataset_id=unicode(args.dataset_id), data_dir=unicode(args.data_dir))
logger.info('Queued dataset job with id = %s' % (job,))