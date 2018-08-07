from modules.setup import Setup, Retrigger
from modules.xdsme import XDSme
from modules.ccp4 import Pointless, Aimless, Truncate
from modules.other import Autorickshaw, CornerResolution
from modules.sadabs import Xds2sad, Sadabs, Xprep, XprepSummary
from beamline import variables as blconfig
from beamline import redis as BLredis

def default_pipeline(base):
    return [
    Setup(suffix='process', detector=blconfig.detector_type),
    XDSme(base, '-a', '--strategy', '--p1-strategy', subtype='p'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme(base, '-3', '-a', '--strategy', '--highest-symm-strategy', subtype='p'),
    XDSme('p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', '-3', '--strategy', '--highest-symm-strategy'),
    Autorickshaw(base)
]

base = 'hsymm'
default = default_pipeline(base)

# chanege xdsme hsymm to only do CORRECT
# add retrigger step to copy data from other processing
def reprocess(base):
    return [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    Retrigger(),
    XDSme(base, '-3', '-a', '--strategy', '--highest-symm-strategy', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', p1=True),
    XDSme(base+'_NOANOM', '-3', '--strategy', '--highest-symm-strategy'),
    Autorickshaw(base)
]
reprocess = reprocess(base)

# to use unit cell and spacegroup
def reprocess_ucsg(base='hsymmucsg'):
    return [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    Retrigger(3),
    XDSme(base, '-3', '--strategy', '-a', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme('p1', '-3', '-a', '--strategy', p1=True),
    XDSme(base+'_NOANOM', '-3', '--strategy'),
    Autorickshaw(base)
]
reprocess_ucsg = reprocess_ucsg()

# for weak, brute, slow, ice options, go from the beginning
def reprocess_from_start(base):
    return [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    XDSme(base, '-a', '--strategy', '--p1-strategy', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme(base, '-3', '-a', '--strategy', '--highest-symm-strategy', subtype='p'),
    XDSme('p1', '-5', '-a', p1=True),
    XDSme(base+'_NOANOM', '-3', '--strategy', '--highest-symm-strategy'),
    Autorickshaw(base)
]

reprocess_from_start = reprocess_from_start(base)

if int (BLredis.get('SMX')) == 1:
    if blconfig.detector_type == 'eiger':
        delphi = 'DELPHI=15'
    else:
        delphi = 'DELPHI=45'

    x = Xds2sad('xds2sad', filename='XDS_ASCII.HKL_p1_noscale')
    w = Sadabs('Sadabs-w', absorber_strength = 'weak')
    m = Sadabs('Sadabs-m', absorber_strength = 'moderate')
    s = Sadabs('Sadabs-s', absorber_strength = 'strong')
    sadabs_steps = [x,w,m,s]
    xp_p1 = Xprep('xprep', filename = 'XDS_ASCII.HKL_p1', suffix = 'p1')
    xp_p1_noscale = Xprep('xprep_p1_scale', filename = 'XDS_ASCII.HKL_p1_noscale', suffix = 'p1_noscale')
    xp_sadabs_w = Xprep('xprep_sadabsw', filename = 'sadabs_w/sad.hkl', suffix = 'sadabs_w')
    xp_sadabs_m = Xprep('xprep_sadabsm', filename = 'sadabs_m/sad.hkl', suffix = 'sadabs_m')
    xp_sadabs_s = Xprep('xprep_sadabss', filename = 'sadabs_s/sad.hkl', suffix = 'sadabs_s')
    xprep_steps = [xp_p1, xp_p1_noscale, xp_sadabs_w, xp_sadabs_m, xp_sadabs_s]
    xp_summary = [XprepSummary()]

    turn_off_correct_scaling = 'NBATCH=1 MINIMUM_I_SIGMA=50 CORRECTIONS=0'

    def default_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, '-a', '--strategy', '--p1-strategy', '-i', delphi, subtype = 'p'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme(base, '-3', '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, subtype='p'),
        XDSme('p1', '-5', '-a', p1=True),
        XDSme('hsymm_noscale', '-5', '-a', '-i', turn_off_correct_scaling),
        XDSme('p1_noscale', '-5', '-a', '-i', turn_off_correct_scaling, p1=True),
        XDSme(base+'_NOANOM', '-3', '--strategy', '--highest-symm-strategy', '-i', delphi),
        Autorickshaw(base)
    ]
    default = default_smx(base)
    default += sadabs_steps
    default += xprep_steps
    default += xp_summary

    def reprocess_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        Retrigger(),
        XDSme('hsymm_noscale', '-5', '-a', '-i', turn_off_correct_scaling, subtype='r'),
        XDSme('p1_noscale', '-5', '-a', '-i', turn_off_correct_scaling, p1=True, subtype='r'),
        XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', p1=True, subtype='r'),
        Autorickshaw(base)
    ]
    reprocess = reprocess_smx(base)
    reprocess += sadabs_steps
    reprocess += xprep_steps
    reprocess += xp_summary

    base2='hsymmucsg'
    def reprocess_ucsg_smx(base2):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base2),
        Retrigger(),
        XDSme(base, '-a', '--strategy', '-i', delphi, subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1_noscale', '-3', '-a', '--strategy', '-i', turn_off_correct_scaling, p1=True, subtype='r'),
        XDSme('hsymm_noscale', '-3', '-a', '--strategy', '-i', turn_off_correct_scaling, subtype='r'),
        Autorickshaw(base)
    ]
    reprocess_ucsg = reprocess_ucsg_smx(base2)
    reprocess_ucsg += sadabs_steps
    reprocess_ucsg += xprep_steps
    reprocess_ucsg += xp_summary

    def reprocess_from_start_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', p1=True, subtype='r'),
        XDSme('p1_noscale', '-5', '-a', '-i', turn_off_correct_scaling, p1=True, subtype='r'),
        XDSme('hsymm_noscale', '-5', '-a', '-i', turn_off_correct_scaling, subtype='r'),
        Autorickshaw(base)
    ]
    reprocess_from_start = reprocess_from_start_smx(base)
    reprocess_from_start += sadabs_steps
    reprocess_from_start += xprep_steps
    reprocess_from_start += xp_summary

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().items()))
