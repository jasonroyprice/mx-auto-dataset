from jinja2 import Environment, FileSystemLoader

#incoming parameters
beamline = 'MX2' # beamline in collection objecxt
energy_in_kev = 13.25
detector = 'eiger' #detector_type in collection object
cryojet_temperature = 110.2
project_dir = '.'

if beamline == 'MX1':
    beamline_text = 'MX1 Beamline Australian Synchrotron'
elif beamline == 'MX2':
    beamline_text = 'MX2 Beamline Australian Synchrotron'
else:
    raise Exception('Unknown beamline')

if detector == 'eiger':
    detector_text = 'Eiger 16M'
elif detector == 'adsc':
    deetector_text = 'ADSC q215'
else:
    raise Exception('Unknown detector')

env = Environment(
    loader=FileSystemLoader('templates'))

template = env.get_template('cx_template.cif')
KEV_TO_ANGSTROM = 12.398420
energy = energy_in_kev/KEV_TO_ANGSTROM

with open('%s/%s' % (project_dir, 'template.cif'), 'w') as template_file:
    template_file.write(template.render(detector=detector_text, beamline=beamline_text, energy=energy, temperature=cryojet_temperature))

