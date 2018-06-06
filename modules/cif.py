from .base import Base
from jinja2 import Environment, FileSystemLoader
from processing.models import Collection, Processing, setup
from beamline import variables as blconfig

def run_test():
    beamline = 'MX2' # beamline in collection objecxt
    energy_in_kev = 13.25
    detector = 'eiger' #detector_type in collection object
    cryojet_temperature = 110.2
    project_dir = '.'
    write_template_file(project_dir, beamline, detector, energy_in_kev, cryojet_temperature)

def write_template_file(project_dir, beamline, detector, energy_in_kev, cryojet_temperature, crystal_in_monochromator):
    if beamline == 'MX1':
        beamline_text = 'MX1 Beamline Australian Synchrotron'
    elif beamline == 'MX2':
        beamline_text = 'MX2 Beamline Australian Synchrotron'
    else:
        raise Exception('Unknown beamline')

    if detector == 'eiger':
        detector_text = 'Dectris Eiger 16M'
    elif detector == 'adsc':
        detector_text = 'ADSC Quantum 210r'
    else:
        raise Exception('Unknown detector')

    env = Environment(
        loader=FileSystemLoader('/xray/software/Python/libraries/mx_auto_dataset/templates'))

    template = env.get_template('cx_template.cif')
    KEV_TO_ANGSTROM = 12.398420
    wavelength = KEV_TO_ANGSTROM/float(energy_in_kev)

    if crystal_in_monochromator == 'DC':
        crystal_in_monochromator = 'Silicon Double Crystal'
    elif crystal_in_monochromator == 'CC':
        crystal_in_monochromator = 'Silicon Channel Cut Crystal'
    else:
        raise Exception('Unknown monochromator type')

    with open('%s/%s' % (project_dir, 'autoprocess.cif'), 'w') as template_file:
        template_file.write(template.render(detector=detector_text, beamline=beamline_text, wavelength='%.6f' % wavelength, temperature=cryojet_temperature, crystal=crystal_in_monochromator))

class Cif(Base):

    def __init__(self, run_name, *args, **kwargs):
        super(Cif, self).__init__()

    def process(self, **kwargs):
        if kwargs['collection_id']:
            coll = Collection(kwargs['collection_id'])
        else:
            setup(blconfig.get_database())
            proc = Processing(kwargs['dataset_id'])
            coll = Collection(str(proc.collection_id.id))

        try:
            cryo_temp = coll.cryo_temperature
        except AttributeError:
            cryo_temp = None
        try:
            crystal_in_monochromator = coll.crystal_in_monochromator
        except AttributeError:
            crystal_in_monochromator = None
        write_template_file(self.project_dir, coll.beamline, coll.detector_type, coll.energy, cryo_temp, crystal_in_monochromator)

if __name__ == '__main__':
    run_test()
