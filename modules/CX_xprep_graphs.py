#------------------------------------------------------------------
# This program reads in Xprep .prp files (e.g. XDS_ASCII.prp)
# To execute this program provide the python script and a file:
#
# $python3.6 /staff/Kate/CX_xprep_graphs.py XDS_ASCII.prp
#
# This will then automatically generate graphs from the log file
# and save this as a .png file in the working directory
#------------------------------------------------------------------
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd
import numpy as np
from .base import Base

def xprep_graphs(project_dir,filename):

    # Open the file and read into a string
    with open(os.path.join(project_dir,filename), 'rt') as myfile:
        contents = myfile.read()

    # Search file for beginning and ending of stats table
    x = re.search(" Inf",contents)
    y = re.search("Merged",contents)
    
    if x is None and y is None:
        pass
    else:
        stats_table = contents[x.start():y.start()].split('\n')

        # Split the rows of the stats table into individual elements
        n = 0
        data = []
        for item in stats_table:
            data.append(stats_table[n].split())
            n+=1

        # Store the stats table as a pandas dataframe and remove last 5 rows (are empty or contain punctuation)
        df = pd.DataFrame(data,columns=['Resolution', 'dash', 'Resolution High',
                                        '#Data','#Theory','%Complete', 'Redundancy',
                                        'Mean I','Mean I/s','R(int)','Rsigma'],dtype=float)
        df.drop(df.tail(5).index,inplace=True)

        x = df['Resolution High']

        y1 = df['R(int)']
        y2 = df['Rsigma']
        y3 = df['%Complete']
        y4 = df['Mean I/s']


        #Graph the following using matplotlib and numpy

        grid = plt.GridSpec(2, 2, wspace=0.2, hspace=0.3)

        plt.subplot(grid[0,0])
        plt.title('Resolution vs R(int)')
        plt.plot(x, y1, '-',color='m')
        plt.xlabel('Resolution')
        plt.ylabel('R(int)')
        plt.gca().invert_xaxis()

        plt.subplot(grid[0,1])
        plt.title('Resolution vs Rsigma')
        plt.plot(x, y2, '-',color='r')
        plt.xlabel('Resolution')
        plt.ylabel('Rsigma')
        plt.gca().invert_xaxis()

        plt.subplot(grid[1,0])
        plt.title('Resolution vs Completeness')
        plt.plot(x, y3, '-',color='g')
        plt.xlabel('Resolution')
        plt.ylabel('Completeness (%)')
        plt.gca().invert_xaxis()

        plt.subplot(grid[1,1])
        plt.title('Resolution vs Mean I/s')
        plt.plot(x, y4, '-',color='b')
        plt.xlabel('Resolution')
        plt.ylabel('Mean I/s')
        plt.gca().invert_xaxis()

        plt.subplots_adjust(bottom=0.1,right=2,top=2)

        # Save the .png graph file into the current directory
        plt.savefig(os.path.join(project_dir,filename.split(".")[0]+'.png'),bbox_inches='tight',pad_inches=0.1)

class XprepGraphs(Base):

    def __init__(self, run_name, *args, **kwargs):
        super(XprepGraphs, self).__init__()
        self.run_name = run_name

    def process(self, **kwargs):
        xprep_graphs(self.project_dir,'XDS_ASCII_p1.prp')
        
