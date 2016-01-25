#!/usr/bin/env python2.7
import os
import sys
import argparse
from config import IS_STAGING

import logbook

from itertools import chain

logger = logbook.Logger('MAIN')

# load modules
import pipelines
from beamline import variables as blconfig

from processing.models import setup, Dataset
setup(blconfig.get_database(staging=IS_STAGING))

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--collection_id')
group.add_argument('--dataset_id')
parser.add_argument('--data_dir')
parser.add_argument('--output_dir')
parser.add_argument('--processing_dir', help="Location of previously run processing directory")

# add parser arguments from all classes inside the pipelines
for clz in set([obj.__class__ for obj in chain(*pipelines.pipelines.values())]):
    try:
        clz.add_args(parser)
    except AttributeError:
        pass

options, unknown_args = parser.parse_known_args()

class Container(object): pass
output = Container()
_input = Container()

if options.dataset_id:
    if options.ice or options.weak or options.slow or options.brute:
        pipeline = pipelines.reprocess_from_start
    elif options.unit_cell and options.space_group:
        pipeline = pipelines.reprocess_ucsg
    else:
        pipeline = pipelines.reprocess
    _input.from_dataset = Dataset(options.dataset_id)
    collection_id = _input.from_dataset.collection_id.id

elif options.collection_id:
    pipeline = pipelines.default
    collection_id = options.collection_id

output.dataset = Dataset.create_from_collection(collection_id)

# modify top level directory - useful for testing with files mounted from sans
if options.data_dir != None:
    from utils import replace_top_directory_level
    last_frame = replace_top_directory_level(output.dataset.last_frame, options.data_dir)
    output.dataset.last_frame = last_frame
    output.dataset.directory = replace_top_directory_level(output.dataset.directory, options.data_dir)
    _input.from_dataset.processing_dir = replace_top_directory_level(_input.from_dataset.processing_dir, options.data_dir)

# if processing_dir is further specified, use it
if options.processing_dir != None:
    _input.from_dataset.processing_dir = replace_top_directory_level(_input.from_dataset.processing_dir,
                                                                     options.processing_dir)

if not os.path.isfile(output.dataset.last_frame):
    logger.error("File %s does not exist" % output.dataset.last_frame)
    sys.exit(1)

for obj in pipeline:
    logger.info("------ RUNNING: %s ------" % obj)
    try:
        obj.input = _input
        obj.output = output
        obj.process(**vars(options))
    except Exception, e:
        logger.error("Failed to run %s: [%s] %s" % (obj.__class__.__name__, e.__class__.__name__, e.message))
        import traceback
        logger.error("traceback: %s" % traceback.format_exc())
        if isinstance(e, EnvironmentError):
            logger.error("More information: %s %s" % (e.strerror, e.errno))

        output.dataset.__dict__.update(completed=True, success=False, status="Failed")
        output.dataset.save()
        break
else:
    output.dataset.__dict__.update(completed=True, success=True, status="Success")
    output.dataset.save()
