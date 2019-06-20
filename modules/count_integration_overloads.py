import sys
import os

def calculate_overloaded_actual(filename):
    f = open(filename, 'r')
    line = f.readline()
    total_ewald = 0
    total_overloaded = 0
    total_strong = 0
    total_rejected = 0
    while line:
        try:
            if not line.split() or line.split()[0] != 'IMAGE':
                line = f.readline()
                continue
            line = f.readline() # get line after headers
            while line.split():
                splitline = line.split()
                novl = splitline[4]
                total_overloaded += int(novl)
                newald = splitline[5]
                total_ewald += int(newald)
                nstrong = splitline[6]
                total_strong += int(nstrong)
                nrej = splitline[7]
                total_rejected += int(nrej)
                line = f.readline()
        except ValueError: # failed integration
            pass
    #IOError is common if there is no file 
    return {'total_ewald': total_ewald, 'total_overloaded': total_overloaded, 'total_strong': total_strong, 'total_rejected': total_rejected}
