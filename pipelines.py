from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate, AimlessPlot, AimlessScalePlot
from modules.other import Autorickshaw, CornerResolution, LinkCorrect, CountOverloads, RunSpreadsheetCalculator
from modules.sadabs import Xds2sad, Sadabs, Xprep, XprepSummary
from modules.CX_xprep_graphs import XprepGraphs
from modules.cif import Cif
from beamline import variables as blconfig

base = 'hsymm'
po = Pointless(base)

def default_pipeline(base):
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
    Autorickshaw(base),
    RunSpreadsheetCalculator(base)
]

default = default_pipeline(base)
# reprocess pipeline (copy of default)
# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
reprocess = [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    Retrigger(),
    XDSme(base, base, '-5', '-a', subtype = 'r'),
    po,
    Aimless(base),
    AimlessPlot(base),
    AimlessScalePlot(base),
    CountOverloads(base),
    XDSme('p1', 'p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', base+'_NOANOM', '-5'),
    Truncate(base),
    LinkCorrect(base),
    Autorickshaw(base),
    RunSpreadsheetCalculator(base)
]

# to use unit cell and spacegroup
reprocess_ucsg = [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    Retrigger(3),
    XDSme(base, 'hsymmucsg', '-3', '-a', subtype = 'r'),
    po,
    Aimless(base),
    AimlessPlot(base),
    AimlessScalePlot(base),
    CountOverloads(base),
    XDSme('p1', 'p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', base+'_NOANOM', '-5'),
    Truncate(base),
    LinkCorrect(base),
    Autorickshaw(base),
    RunSpreadsheetCalculator(base)
]

# for weak, brute, slow, ice options, go from the beginning
reprocess_from_start = [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    XDSme(base, base, '-a', subtype = 'r'),
    po,
    Aimless(base),
    AimlessPlot(base),
    AimlessScalePlot(base),
    CountOverloads(base),
    XDSme('p1', 'p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', base+'_NOANOM', '-5'),
    Truncate(base),
    LinkCorrect(base),
    Autorickshaw(base),
    RunSpreadsheetCalculator(base)
]

from beamline import redis as BLredis
if int (BLredis.get('SMX')) == 1:
    if blconfig.detector_type == 'eiger': #TODO get this information from collection object
        delphi = 'DELPHI=15'
    else:
        delphi = 'DELPHI=45'

    p1n = 'p1_noscale'
    hsn = 'hsymm_noscale'

    po = Pointless(base, nonchiral=True)

    default = [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, base, '-a', '-i', delphi, subtype = 'p'),
        po,
        Aimless(base),
        AimlessPlot(base),
        AimlessScalePlot(base),
        CountOverloads(base),
        XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True),
        XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0'),
        XDSme('p1', 'p1', '-5', '-a', p1=True),
        Truncate(base),
        LinkCorrect(base),
        Autorickshaw(base),
        RunSpreadsheetCalculator(base)
    ]

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

    reprocess = [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        Retrigger(),
        XDSme(base, base, '-5', '-a', '-i', delphi, subtype = 'r'),
        po,
        Aimless(base),
        AimlessPlot(base),
        AimlessScalePlot(base),
        CountOverloads(base),
        XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype='r'),
        XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r'),
        XDSme('p1', 'p1', '-5', '-a', p1=True),
        Truncate(base),
        LinkCorrect(base),
        Autorickshaw(base),
        RunSpreadsheetCalculator(base)
    ]
    reprocess += sadabs_steps
    reprocess += xprep_steps
    reprocess.append(xp_summary)
    reprocess.append(xp_graphs)

    reprocess_ucsg = [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        Retrigger(3),
        XDSme(base, 'hsymmucsg', '-3', '-a', '-i', delphi, subtype = 'r'),
        po,
        Aimless(base),
        AimlessPlot(base),
        AimlessScalePlot(base),
        CountOverloads(base),
        XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype='r'),
        XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r'),
        XDSme('p1', 'p1', '-5', '-a', p1=True),
        Truncate(base),
        LinkCorrect(base),
        Autorickshaw(base),
        RunSpreadsheetCalculator(base)
    ]
    reprocess_ucsg += sadabs_steps
    reprocess_ucsg += xprep_steps
    reprocess_ucsg.append(xp_summary)
    reprocess_ucsg.append(xp_graphs)

    reprocess_from_start = [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, base, '-a', '-i', delphi, subtype = 'r'),
        po,
        Aimless(base),
        AimlessPlot(base),
        AimlessScalePlot(base),
        CountOverloads(base),
        XDSme(p1n, p1n, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', p1=True, subtype='r'),
        XDSme(hsn, hsn, '-5', '-a', '-i', 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0', subtype='r'),
        XDSme('p1', 'p1', '-5', '-a', p1=True),
        Truncate(base),
        LinkCorrect(base),
        Autorickshaw(base),
        RunSpreadsheetCalculator(base)
    ]
    reprocess_from_start += sadabs_steps
    reprocess_from_start += xprep_steps
    reprocess_from_start.append(xp_summary)
    reprocess_from_start.append(xp_graphs)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().items()))
