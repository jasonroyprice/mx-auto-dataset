#!/usr/bin/env python2.7
import os
import sys
import argparse

import logbook

from itertools import chain
#loghandle = logbook.FileHandler('/tmp/test.log', bubble=True)
#loghandle.push_application()

logger = logbook.Logger('MAIN')

# load modules
import pipelines
from beamline import variables as blconfig

from processing.models import setup, Dataset
setup(blconfig.get_database(staging=True))

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--collection_id')
group.add_argument('--dataset_id')
parser.add_argument('--data_dir')

for clz in set([obj.__class__ for obj in chain(*pipelines.pipelines.values())]):
    try:
        clz.add_args(parser)
    except AttributeError:
        pass

options, unknown_args = parser.parse_known_args()

### process unknown args
#kwargs = {}
#for arg in unknown_args:
#    if arg.startswith('--'): # O
#        opt = arg[2:]
#        kwargs[opt] = []
#    else: # V
#        kwargs[opt].append(arg)
#
### remove list from single value args
#for k,v in kwargs.iteritems():
#    if len(v) == 1:
#        kwargs[k] = v[0]
#
#kwargs.update(vars(options))

class Container(object): pass
output = Container()
_input = Container()

if options.dataset_id:
    #pipeline = pipelines.default
    pipeline = pipelines.reprocess
    _input.from_dataset = Dataset(options.dataset_id)
    collection_id = _input.from_dataset.collection_id.id

elif options.collection_id:
    pipeline = pipelines.default
    collection_id = options.collection_id

output.dataset = Dataset.create_from_collection(collection_id)

# modify top level directory - useful for testing with files mounted from sans
datadir = options.data_dir
if datadir != None:
    splitpath = output.dataset.last_frame.split(os.sep)
    splitpath[1] = datadir
    output.dataset.last_frame = os.sep.join(splitpath)

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

        output.dataset.__dict__.update(completed=True, success=False, status="Failed")
        output.dataset.save()
        break
else:
    output.dataset.__dict__.update(completed=True, success=True, status="Success")
    output.dataset.save()
