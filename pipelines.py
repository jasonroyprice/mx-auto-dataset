from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate, AimlessPlot, AimlessScalePlot
from modules.other import Autorickshaw, CornerResolution, LinkCorrect, CountOverloads
from modules.sadabs import Xds2sad, Sadabs, Xprep, XprepSummary
from modules.CX_xprep_graphs import XprepGraphs
from modules.cif import Cif
from beamline import variables as blconfig
def default_pipeline(base):
    from beamline import redis as BLredis
    if int(BLredis.get('SMX')) == 1:
        po = Pointless(base, nonchiral=True)
    else:
        po = Pointless(base)
    return [
    Setup(suffix='process', detector=blconfig.detector_type),
    XDSme(base, base, '-a', subtype = 'p'),
    po,
    Aimless(base),
    AimlessPlot(base),
    AimlessScalePlot(base),
    CountOverloads(base),
    XDSme('p1', 'p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', base+'_NOANOM', '-5'),
    Truncate(base),
    LinkCorrect(base),
    Autorickshaw(base)
]

base = 'hsymm'
default = default_pipeline(base)
# reprocess pipeline (copy of default)
# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
reprocess = list(default)
reprocess[0] = Setup(suffix='retrigger', detector=blconfig.detector_type)
reprocess[1] = XDSme(base, base, '-5', '-a', subtype = 'r')
reprocess.insert(1, Retrigger())

# to use unit cell and spacegroup
reprocess_ucsg = default_pipeline(base)
reprocess_ucsg[0] = Setup(suffix = 'retrigger', detector=blconfig.detector_type)
reprocess_ucsg[1] = XDSme(base, 'hsymmucsg', '-3', '-a', subtype = 'r')
reprocess_ucsg.insert(1, Retrigger(3))

# for weak, brute, slow, ice options, go from the beginning
reprocess_from_start = list(default)
reprocess_from_start[0] = Setup(suffix = 'retrigger', detector=blconfig.detector_type)
reprocess_from_start[1] = XDSme(base, base, '-a', subtype = 'r')

from beamline import redis as BLredis
if int (BLredis.get('SMX')) == 1:
    default.insert(1, CornerResolution(base))

    if blconfig.detector_type == 'eiger':
        delphi = 'DELPHI=15'
    else:
        delphi = 'DELPHI=45'
    from_start_delphi = XDSme(base, base, '-a', '-i', delphi, subtype='p')
    default[2] = from_start_delphi

    p1n = 'p1_noscale'
    hsn = 'hsymm_noscale'

    p1_noscale = XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True)
    hsymm_noscale = XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0')
    del default[8:9]
    default.insert(7, hsymm_noscale)
    default.insert(7, p1_noscale)
    c = Cif(base)
    x = Xds2sad('xds2sad', filename='XDS_ASCII.HKL_p1_noscale')
    w = Sadabs('Sadabs-w', absorber_strength = 'weak')
    m = Sadabs('Sadabs-m', absorber_strength = 'moderate')
    s = Sadabs('Sadabs-s', absorber_strength = 'strong')
    sadabs_steps = [c,x,w,m,s]
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

    xp_graphs = XprepGraphs(base)
    default.append(xp_graphs)

    p1_noscale_reprocess = XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype= 'r')
    hsymm_noscale_reprocess = XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r')
    reprocess.insert(1, CornerResolution(base))
    del reprocess[10:11]
    reprocess.insert(4, hsymm_noscale_reprocess)
    reprocess.insert(4, p1_noscale_reprocess)
    reprocess += sadabs_steps
    reprocess += xprep_steps
    reprocess.append(xp_summary)
    reprocess.append(xp_graphs)

    p1_noscale_ucsg = XDSme(p1n, p1n, '-3', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype= 'r')
    hsymm_noscale_ucsg = XDSme(hsn, hsn, '-3', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r')
    reprocess_ucsg.insert(1, CornerResolution(base))
    del reprocess_ucsg[10:11]
    reprocess_ucsg.insert(4, hsymm_noscale_ucsg)
    reprocess_ucsg.insert(4, p1_noscale_ucsg)
    reprocess_ucsg += sadabs_steps
    reprocess_ucsg += xprep_steps
    reprocess_ucsg.append(xp_summary)
    reprocess_ucsg.append(xp_graphs)

    from_start_delphi_reprocess = XDSme(base, base, '-a', '-i', delphi, subtype='r')
    reprocess_from_start.insert(1, CornerResolution(base))
    del reprocess_from_start[9:10]
    reprocess_from_start[2] = from_start_delphi_reprocess
    reprocess_from_start.insert(7, p1_noscale_reprocess)
    reprocess_from_start.insert(8, hsymm_noscale_reprocess)
    reprocess_from_start += sadabs_steps
    reprocess_from_start += xprep_steps
    reprocess_from_start.append(xp_summary)
    reprocess_from_start.append(xp_graphs)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().items()))
