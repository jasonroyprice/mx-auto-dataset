import logbook
logger = logbook.Logger(__name__)

__author__ = 'aishimaj'
from beamline import get_database
from mx_auto_dataset import dataset
from processing.models import setup
import argparse

setup(get_database(staging=True))

parser = argparse.ArgumentParser()
parser.add_argument("--id", help="collection ID of dataset to reprocess")
parser.add_argument("--data_dir", help="top-level directory name (like /data for most data)")
args = parser.parse_args()
if not args.id:
    import sys
    sys.exit("no ID provided, aborting")
job = dataset.delay(collection_id=args.id, data_dir=args.data_dir)
logger.info('Queued dataset job with id = %s' % (job,))