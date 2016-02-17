#!/usr/bin/env python
# inject new libraries onto path
import sys
import shutil

try: 
    sys.path.index('/xray/progs/Python/libraries')
except (ValueError, TypeError):
    sys.path.insert(0,'/xray/progs/Python/libraries')
    
import re, subprocess, tempfile, os, beamline
from xml.etree import ElementTree
from beamline import redis as redis
from beamline import variables as mxvars
import json

# hack to get new dir for autorickshaw

def pathsplit():
    dirname = os.getcwd()
    pathsplit = dirname.split('/')
    return pathsplit

def get_uniquedir(listD):
    if len(listD) >= 7:
        if listD[6] == 'dataset':
            print "autorick parse debug2:"
            print listD[7]
            return listD[7]
        else:
            print "autorick parse debug3:"
            print "could not find dataset in element 6"
            return None
    else:
        print "autorick parse debug4:"
        print "number of elements smaller than 8"
        return None

def runall():
    listD = pathsplit()
    unique = get_uniquedir(listD)
    return unique

# get setup in temp zone
try:
    os.makedirs('AR')
except EnvironmentError:
    pass


if runall():
    try:
        newdir = "%s/rickshaw/%s/" % (mxvars.AUTO_DIR,runall())
        os.makedirs(newdir)
        os.symlink(newdir,'AR')
    except EnvironmentError:
        pass  
else:
    print "Something funny happened while trying to figure out the unique dir. Not parsing this file"
    print runall()
    sys.exit()


newkey = 'shelx:trigger' 
correct_file = "CORRECT.LP_hsymm"
table_header = "SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION"
table_offest = 4 #start of data
table_size = 14 #total table size


if redis.get(newkey):
    print 'clear redis anom key'
    print redis.get(newkey)
    redis.set(newkey,json.dumps('off'))
else:
    print "redis was empty"
    redis.set(newkey,json.dumps('off'))

anon_cutoff = 15
anon_col = 11
res_col = 0

get_number = lambda x: int(re.sub(r'[^-\d.]+', '', x))

# get table from correct file
try:
    with open(correct_file, 'r') as correct:
        lines = correct.readlines()
        table_start = [i for i,x in enumerate(lines) if x.strip() == table_header][-1]
        table = [x.strip().split() for x in lines[table_start+table_offest : table_start+table_size]]
except EnvironmentError:
    print "Unable to open: %s" % correct_file
    sys.exit(1)
# get max resolution from second last row of table
r = float(table[-2][res_col])

# get max resolution that has anon signal above anon_cutoff
try:
    cr = float([x[res_col] for x in table if ('total' not in x[res_col]) and (get_number(x[anon_col]) >= anon_cutoff)][-1])
except IndexError:
    # can't find a cr as no anon signal
    cr = float('inf')

# diff
diff = cr -r

# get the row with the highest signal    
anon_col = [get_number(x[anon_col]) for x in table]
max_anon_row = anon_col.index(max(anon_col))

# print results
print
for line in table:
    for item in line:
        print "%7s" % item,
    print
print
print "   Max Resolution: %s" % (r, )
print "Cutoff Resolution: %s" % (cr, )
print "       Difference: %s" % (diff, )
print "   Max Signal Row: %s" % (max_anon_row, )

# Filter out small molecule data
hkl_file = "XDS_ASCII.HKL_hsymm"
with open(hkl_file) as f:
    for line in f:
    	if 'X-RAY_WAVELENGTH' in line:
		wavelength = float(line.split()[1])
	if 'UNIT_CELL_CONSTANTS' in line:
		a = float(line.split()[1])
		b = float(line.split()[2])
		c = float(line.split()[3])
		cell = a*b*c
 
if wavelength < 0.75 and cell < 16000 :
	m = int(0)
else:
	m= int(1)


# parsing conditions apply
if diff > 1 or max_anon_row > 1 or m < 1:
    print "Data does not met requirements for automatic Autorickshaw launch for SAD phasing."
    sys.exit(0)
    
if redis.get(newkey):
    print "Anom present. Setting redis key"
    redis.set(newkey,json.dumps('on'))


# setup directory
directory = os.path.join(beamline.variables.AUTO_DIR, 'rickshaw')
try:
    os.makedirs(directory)
except EnvironmentError:
    pass


# autorick conversions

xdsconv_out = "%s/temp.cv" % newdir
f2mtz_out = "%s/temp.mtz" % newdir
cad_out = "%s/output.mtz" % newdir
#mtz2sca_in = os.path.splitext(cad_out)[0]
mtz2sca_in = os.path.splitext("aimless_hsymm.mtz")[0]

pointless_in = "%s.sca" % mtz2sca_in
pointless_xmlout = '%s/pointless_output.xml' % newdir

# pointless
subprocess.check_output(['pointless', 'XDSIN', hkl_file, 'XMLOUT', pointless_xmlout], stderr=subprocess.STDOUT)

# harvest SG
tree = ElementTree.parse(pointless_xmlout)
SG = tree.findtext('.//BestSolution/GroupName')
SG = "".join(SG.split())
if SG == "P1211":
	SG = "P21"

if SG == "C121":
	SG = "C2"
	
# autorickshaw variables
ar_vars = {
    'beamline' : beamline.variables.ID,
    'EPN' : beamline.variables.EPN,
    'datafile1' : pointless_in,
    'SG' :     SG,
    'keeps': 'AR_Developers',
    'ver': 'completeversion',
    'meth':  'SAD',
    'email': 'skpanjikar@gmail.com',
    'directory': newdir
}

if os.path.isfile("aimless_hsymm.mtz"):
	# mtz2sca
	subprocess.check_output(['mtz2sca', mtz2sca_in], stderr=subprocess.STDOUT)
	shutil.copy('aimless_hsymm.sca', newdir +'aimless_hsymm.sca')
else:
	print "aimless_hsymm.mtz is missing"
	sys.exit(0)

# build AR command
os.chdir(newdir)
command = ['python2.7', '/xray/progs/autorick/DPS2AR.py']
for (key, value) in ar_vars.iteritems():
    command.append(key)
    command.append(value)
print
print ar_vars
print ' '.join(command)

subprocess.call(command, stderr=subprocess.STDOUT)
