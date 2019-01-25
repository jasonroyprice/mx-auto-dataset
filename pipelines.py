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
    XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '--skip_defpix', subtype='p'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '--skip_defpix', p1=True),
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
    XDSme(base, '-3', '-a', '--strategy', '--highest-symm-strategy', '--skip_defpix', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '--skip_defpix', p1=True),
    Autorickshaw(base)
]
reprocess = reprocess(base)

# to use unit cell and spacegroup
def reprocess_ucsg(base='hsymmucsg'):
    return [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    Retrigger(3),
    XDSme(base, '-3', '--strategy', '-a', '--skip_defpix', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    Autorickshaw(base)
]
reprocess_ucsg = reprocess_ucsg()

# for weak, brute, slow, ice options, go from the beginning
def reprocess_from_start(base):
    return [
    Setup(suffix='retrigger', detector=blconfig.detector_type),
    XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '--skip_defpix', subtype = 'r'),
    Pointless(base),
    Aimless(base),
    Truncate(base),
    XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '--skip_defpix', p1=True),
    Autorickshaw(base)
]

reprocess_from_start = reprocess_from_start(base)

if int (BLredis.get('SMX')) == 1:
    if blconfig.detector_type == 'eiger':
        delphi = 'DELPHI=15'
    else:
        delphi = 'DELPHI=45'

    def default_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, '--skip_defpix', subtype = 'p'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '-i', delphi, '--skip_defpix', subtype='p', p1=True),
        Autorickshaw(base)
    ]
    default = default_smx(base)

    def reprocess_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        Retrigger(),
        XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, '--skip_defpix', subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '-i', delphi, '--skip_defpix', p1=True, subtype='r'),
        Autorickshaw(base)
    ]
    reprocess = reprocess_smx(base)

    base2='hsymmucsg'
    def reprocess_ucsg_smx(base2):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base2),
        Retrigger(),
        XDSme(base, '-a', '--strategy', '-i', delphi, '--skip_defpix', subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme(base, '-3', '--strategy', '-i', delphi, '--skip_defpix', subtype='r'),
        Autorickshaw(base)
    ]
    reprocess_ucsg = reprocess_ucsg_smx(base2)

    def reprocess_from_start_smx(base):
        return [
        Setup(suffix='process', detector=blconfig.detector_type),
        CornerResolution(base),
        XDSme(base, '-a', '--strategy', '--highest-symm-strategy', '-i', delphi, '--skip_defpix', subtype='r'),
        Pointless(base, nonchiral=True),
        Aimless(base),
        Truncate(base),
        XDSme('p1', '-3', '-a', '--strategy', '--p1-strategy', '--skip_defpix', p1=True, subtype='r'),
        Autorickshaw(base)
    ]
    reprocess_from_start = reprocess_from_start_smx(base)

pipelines = dict(filter(lambda x: isinstance(x[1], list), locals().items()))
