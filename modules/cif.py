from .base import Base
from jinja2 import Environment, FileSystemLoader
import epics
from processing.models import Collection

def run_test():
    beamline = 'MX2' # beamline in collection objecxt
    energy_in_kev = 13.25
    detector = 'eiger' #detector_type in collection object
    cryojet_temperature = 110.2
    project_dir = '.'
    write_template_file(project_dir, beamline, detector, energy_in_kev, cryojet_temperature)

def write_template_file(project_dir, beamline, detector, energy_in_kev, cryojet_temperature):
    if beamline == 'MX1':
        beamline_text = 'MX1 Beamline Australian Synchrotron'
    elif beamline == 'MX2':
        beamline_text = 'MX2 Beamline Australian Synchrotron'
    else:
        raise Exception('Unknown beamline')

    if detector == 'eiger':
        detector_text = 'Eiger 16M'
    elif detector == 'adsc':
        detector_text = 'ADSC q215'
    else:
        raise Exception('Unknown detector')

    env = Environment(
        loader=FileSystemLoader('/xray/software/Python/libraries/mx_auto_dataset/templates'))

    template = env.get_template('cx_template.cif')
    KEV_TO_ANGSTROM = 12.398420
    energy = float(energy_in_kev)/KEV_TO_ANGSTROM

    with open('%s/%s' % (project_dir, 'template.cif'), 'w') as template_file:
        template_file.write(template.render(detector=detector_text, beamline=beamline_text, energy=energy, temperature=cryojet_temperature))

class Cif(Base):

    def __init__(self, run_name, *args, **kwargs):
        super(Cif, self).__init__()

    def process(self, **kwargs):
        coll = Collection(kwargs['collection_id'])
        if coll.beamline == 'MX2':
            cj_temp_base = 'SR03ID01CJ01'
        elif coll.beamline == 'MX1':
            cj_temp_base = 'SR03BM01CJ01'
        else:
            raise Exception('unknown beamline - cannot determine cryojet base PV name')
        cryojet_temperature = epics.PV('%s:SAMPLET_MON' % (cj_temp_base)).get()
        write_template_file(self.project_dir, coll.beamline, coll.detector_type, coll.energy, cryojet_temperature)

if __name__ == '__main__':
    run_test()
