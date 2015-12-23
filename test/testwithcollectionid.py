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
args = parser.parse_args()
if not args.id:
    import sys
    sys.exit("no ID provided, aborting")
job = dataset.delay(collection_id=args.id)
logger.info('Queued dataset job with id = %s' % (job,))