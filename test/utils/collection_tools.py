__author__ = 'aishimaj'
from beamline import variables as blconfig
from processing.models import setup, Collection

def _copy_collection_by_id(collection_id, staging):
    setup(blconfig.get_database(staging=staging))

    c=Collection(collection_id)
    c.reload()
    setup(blconfig.get_database(staging=not staging))
    newc = Collection()
    newc.__dict__ = c.__dict__
    newc._id = None
    newc.save()
    return newc.dbref

def copy_to_staging_by_id(collection_id):
    '''
    copy a collection existing in deployment database to staging
    :param collection_id:
    :return:
    '''
    return _copy_collection_by_id(collection_id, False)

def copy_from_staging_by_id(collection_id):
    '''
    copy a collection from staging to deployment database
    :param collection_id:
    :return:
    '''
    return _copy_collection_by_id(collection_id, True)

def copy_all_collections_from_epn_to_staging(epn):
    setup(blconfig.get_database(staging=False))
    from processingDB import VisitStats
    v=VisitStats()
    (all_coll, all_proc) = v.get_epn_info(epn)
    iddict = {}
    for coll in all_coll:
        #print "copying %s to staging..." % coll['_id']
        oldid=str(coll['_id'])
        newid = copy_to_staging_by_id(coll['_id'])
        iddict[oldid] = newid
    return iddict
