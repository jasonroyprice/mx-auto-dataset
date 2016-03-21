__author__ = 'aishimaj'
from beamline import variables as blconfig
from processing.models import setup, Processing

def _copy_processing_by_obj(processing, staging):
    setup(blconfig.get_database(staging=staging))
    newp = Processing()
    newp.__dict__ = processing
    newp._id = None
    newp.save()

def copy_all_processings_from_epn_to_staging(epn, collidmap):
    from processingDB import VisitStats
    v=VisitStats()
    (all_coll, all_proc) = v.get_epn_info(epn)
    for proc in all_proc:
        try:
            id = str(proc['collection_id'].id)
            proc['collection_id'] = collidmap[id] #point to new collection in staging
            _copy_processing_by_obj(proc, True)
        except KeyError:
            pass #this will currently prevent indexings from being transferred as they have no collection ID!

def copy_coll_proc_from_epn(epn):
    from collection_tools import copy_all_collections_from_epn_to_staging
    collidmap = copy_all_collections_from_epn_to_staging(epn)
    copy_all_processings_from_epn_to_staging(epn, collidmap)

#when run on the processing development computer, links recent visits to the current /data/ directory
#this will hopefully allow us to run some retriggerings
def link_60days_directories(epn):
    import os
    sans_dir = "/sans/60days/%s" % epn
    local_data_dir = "/data/%s" %epn
    if os.path.exists(sans_dir):
        if not os.path.exists(local_data_dir):
            os.makedirs(local_data_dir)
        os.symlink(sans_dir+os.sep+"frames", local_data_dir+os.sep+"frames")
        os.symlink(sans_dir+os.sep+"home", local_data_dir+os.sep+"home")
    else:
        print sans_dir,"does not exist"