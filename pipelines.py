from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate
from modules.other import Autorickshaw, CornerResolution
from modules.sadabs import Xds2sad, Sadabs, Xprep, XprepSummary

def default_pipeline(base):
    from beamline import redis as BLredis
    if int(BLredis.get('SMX')) == 1:
        po = Pointless(base, nonchiral=True)
    else:
        po = Pointless(base)
    return [
    Setup(suffix='process'),
    XDSme(base, '-a', subtype = 'p'),
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
reprocess[0] = Setup(suffix='retrigger')
reprocess[1] = XDSme(base, '-5', '-a', subtype = 'r')
reprocess.insert(1, Retrigger())

# to use unit cell and spacegroup
base2 = 'hsymmucsb'
reprocess_ucsg = default_pipeline(base2)
reprocess_ucsg[0] = Setup(suffix = 'retrigger')
reprocess_ucsg[1] = XDSme(base2, '-3', '-a', subtype = 'r')
reprocess_ucsg.insert(1, Retrigger(3))

# for weak, brute, slow, ice options, go from the beginning
reprocess_from_start = list(default)
reprocess_from_start[0] = Setup(suffix = 'retrigger')
reprocess_from_start[1] = XDSme(base, '-a', subtype = 'r')

from beamline import redis as BLredis
if int (BLredis.get('SMX')) == 1:
    default.insert(1, CornerResolution(base))
    from_start_delphi = XDSme(base, '-a', '-i', 'DELPHI=45', subtype='p')
    default[2] = from_start_delphi
    p1_noscale = XDSme('p1_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True)
    hsymm_noscale = XDSme('hsymm_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0')
    default[4] = p1_noscale
    default.insert(4, hsymm_noscale)
    x = Xds2sad('xds2sad', filename='XDS_ASCII.HKL_p1_noscale')
    w = Sadabs('Sadabs-w', absorber_strength = 'weak')
    m = Sadabs('Sadabs-m', absorber_strength = 'moderate')
    s = Sadabs('Sadabs-s', absorber_strength = 'strong')
    sadabs_steps = [x,w,m,s]
    default += sadabs_steps
    xp_p1 = Xprep('xprep', filename = 'XDS_ASCII.HKL_p1', suffix = 'p1')
    xp_p1_noscale = Xprep('xprep_p1_scale', filename = 'XDS_ASCII.HKL_p1_noscale', suffix = 'p1_noscale')
    xp_sadabs_w = Xprep('xprep_sadabsw', filename = 'sadabs_w/sad.hkl', suffix = 'sadabs_w')
    xp_sadabs_m = Xprep('xprep_sadabsm', filename = 'sadabs_m/sad.hkl', suffix = 'sadabs_m')
    xp_sadabs_s = Xprep('xprep_sadabss', filename = 'sadabs_s/sad.hkl', suffix = 'sadabs_s')

    xprep_steps = [xp_p1, xp_p1_noscale, xp_sadabs_w, xp_sadabs_m, xp_sadabs_s]
    default += xprep_steps

    xp_summary = XprepSummary()
    default.append(xp_summary)

    p1_noscale_reprocess = XDSme('p1_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype= 'r')
    hsymm_noscale_reprocess = XDSme('hsymm_noscale', '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r')
    reprocess.insert(1, CornerResolution(base))
    del reprocess[5:6]
    reprocess.insert(3, hsymm_noscale_reprocess)
    reprocess.insert(4, p1_noscale_reprocess)
    reprocess += sadabs_steps
    reprocess += xprep_steps
    reprocess.append(xp_summary)

    p1_noscale_ucsg = XDSme('p1_noscale', '-3', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype= 'r')
    hsymm_noscale_ucsg = XDSme('hsymm_noscale', '-3', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r')
    reprocess_ucsg.insert(1, CornerResolution(base2))
    del reprocess_ucsg[3:6]
    reprocess_ucsg.insert(3, hsymm_noscale_ucsg)
    reprocess_ucsg.insert(3, p1_noscale_ucsg)
    reprocess_ucsg += sadabs_steps
    reprocess_ucsg += xprep_steps
    reprocess_ucsg.append(xp_summary)

    from_start_delphi_reprocess = XDSme(base, '-a', '-i', 'DELPHI=45', subtype='r')
    reprocess_from_start.insert(1, CornerResolution(base))
    del reprocess_from_start[4:5]
    reprocess_from_start[2] = from_start_delphi_reprocess
    reprocess_from_start.insert(4, p1_noscale_reprocess)
    reprocess_from_start.insert(5, hsymm_noscale_reprocess)
    reprocess_from_start += sadabs_steps
    reprocess_from_start += xprep_steps
    reprocess_from_start.append(xp_summary)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().iteritems()))
