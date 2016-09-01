from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate
from modules.other import Autorickshaw, CornerResolution
from modules.sadabs import Xds2sad, Sadabs, Xprep

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

from beamline import redis as BLredis
if int (BLredis.get('SMX')) == 1:
    default.insert(1, CornerResolution(base))
    default[2] = XDSme(base, '-a', '-i', 'DELPHI=45', subtype='p')
    p1_noscale = XDSme('p1_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True)
    hsymm_noscale = XDSme('hsymm_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0')
    default[4] = p1_noscale
    default.insert(4, hsymm_noscale)
    x = Xds2sad('xds2sad', filename='XDS_ASCII.HKL_p1_noscale')
    w = Sadabs('Sadabs-w', absorber_strength = 'weak')
    m = Sadabs('Sadabs-m', absorber_strength = 'moderate')
    s = Sadabs('Sadabs-s', absorber_strength = 'strong')
    default.append(x)
    default.append(w)
    default.append(m)
    default.append(s)
    xp_p1 = Xprep('xprep', filename = 'XDS_ASCII.HKL_p1', suffix = 'p1')
    xp_p1_noscale = Xprep('xprep_p1_scale', filename = 'XDS_ASCII.HKL_p1_noscale', suffix = 'p1_noscale')
    xp_sadabs_w = Xprep('xprep_sadabsw', filename = 'sadabs_w/sad.hkl', suffix = 'sadabs_w')
    xp_sadabs_m = Xprep('xprep_sadabsm', filename = 'sadabs_m/sad.hkl', suffix = 'sadabs_m')
    xp_sadabs_s = Xprep('xprep_sadabss', filename = 'sadabs_s/sad.hkl', suffix = 'sadabs_s')

    default.append(xp_p1)
    default.append(xp_p1_noscale)
    default.append(xp_sadabs_w)
    default.append(xp_sadabs_m)
    default.append(xp_sadabs_s)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().iteritems()))
