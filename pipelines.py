from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate

default = [
    Setup(),
    XDSme('hsymm', '-a'),
    XDSme('p1', '-5', '-a', p1=True),
    XDSme('hsymm_NOANOM', '-5'),
    Pointless('hsymm'),
    Aimless('hsymm'),
    Truncate('hsymm')
]

# reprocess pipeline (copy of default)
# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
reprocess = list(default)
reprocess[1] = XDSme('hsymm', '-5', '-a')
reprocess.insert(1, Retrigger())


pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().iteritems()))
