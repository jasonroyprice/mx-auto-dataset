from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate
from modules.other import Autorickshaw, CornerResolution
from modules.diffpics_with_preds import DiffPicsWithPreds

def default_pipeline(base):
    from beamline import redis as BLredis
    if int(BLredis.get('SMX')) == 1:
        po = Pointless(base, nonchiral=True)
    else:
        po = Pointless(base)
    return [
    Setup(),
    XDSme(base, '-a'),
    XDSme('p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', '-5'),
    po,
    Aimless(base),
    Truncate(base),
    Autorickshaw(base)
]

base = 'hsymm'
default_no_diffpics = default_pipeline(base)
diffpics = DiffPicsWithPreds(base)
default = list(default_no_diffpics)
default.insert(2, diffpics)
# reprocess pipeline (copy of default)
# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
reprocess = list(default_no_diffpics)
reprocess[1] = XDSme(base, '-5', '-a')
reprocess.insert(1, Retrigger())

# to use unit cell and spacegroup
base2 = 'hsymmucsb'
reprocess_ucsg = default_pipeline(base2)
reprocess_ucsg[1] = XDSme(base2, '-3', '-a')
reprocess_ucsg.insert(1, Retrigger(3))

# for weak, brute, slow, ice options, go from the beginning
reprocess_from_start = list(default_no_diffpics)

from beamline import redis as BLredis
if int (BLredis.get('SMX')) == 1:
    default.insert(1, CornerResolution(base))

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().iteritems()))
