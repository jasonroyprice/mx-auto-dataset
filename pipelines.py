from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate

def default_pipeline(base):
    return [
    Setup(),
    XDSme(base, '-a'),
    XDSme('p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', '-5'),
    Pointless(base),
    Aimless(base),
    Truncate(base)
]

base = 'hsymm'
default = default_pipeline(base)
# reprocess pipeline (copy of default)
# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
reprocess = list(default)
reprocess[1] = XDSme(base, '-5', '-a')
reprocess.insert(1, Retrigger())

# to use unit cell and spacegroup
base2 = 'hsymmucsb'
reprocess_ucsg = default_pipeline(base2)
reprocess_ucsg[1] = XDSme(base2, '-3', '-a')
reprocess_ucsg.insert(1, Retrigger(3))

# for weak, brute, slow, ice options, go from the beginning
reprocess_from_start = list(default)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().iteritems()))
