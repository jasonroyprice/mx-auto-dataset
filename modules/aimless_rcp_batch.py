import sys
import os

#below assumes that ccp4 is set up
smartie_path = '%s/share/smartie' % os.environ['CCP4']
sys.path.append(smartie_path)

import click
import smartie
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import tempfile
from beamline import redis

def extract_rcp_batch(directory, filename):
    logfile = smartie.parselog('%s/%s' % (directory, filename))
    table = logfile.program(0).tables('Radiation damage analysis for run   1')[0]
    batch = table.col('Batch')
    rcp = table.col('Rcp')
    cmposs = table.col('CmPoss')
    return batch, rcp, cmposs

def plot_rcp_batch(batch, rcp, cmposs, filename, write_to_redis, redis_key):
    if write_to_redis and not redis_key:
        raise TypeError('if writing to redis, redis_key must be defined')
    plots = []
    fig, ax1 = plt.subplots()
    ax1.set_title('Rcp vs. batch')
    ax1.set_xlabel('batch')
    xaxis = batch
    yaxis = [float(i) if i is not '-' else None for i in rcp] # numbers come out of tables as text
    yaxis2 = [float(i) if i is not '-' else None for i in cmposs]
    plots.append(ax1)
    ax = plots[-1]
    ax.plot(xaxis, yaxis2, 'blue', label='CmPoss', color='b')
    ax.set_ylabel('CmPoss', color='b')
    ax.tick_params('y', colors='b')
    ax.set_ylim(0, 1.1)

    ax2 = ax.twinx()
    ax2.plot(xaxis, yaxis, 'red', label='Rcp', color='r')
    ax2.set_ylabel('Rcp', color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_ylim(0, max(yaxis) * 2)

    if write_to_redis and redis_key:
        try:
            tmpdirectory = tempfile.mkdtemp()
            tmpfilename = 'rcp.png'
            tmppath = os.path.join(tmpdirectory, tmpfilename)
            plt.savefig(tmppath, format='png')
            with open(tmppath,'r') as tmpfile:
                ex = 60*60*24*30*3 # seconds in 3 months
                redis.set(redis_key, tmpfile.read(),ex=ex)
        finally:
            os.remove(tmppath)
            os.rmdir(tmpdirectory)
    else:
        plt.savefig(filename, format='png')
    plt.close()

@click.command()
@click.option('--directory')
@click.option('--filename', default='aimless.log')
@click.option('--output_filename', default='aimless.png')
@click.option('--write_to_redis', type=bool, default=False, help='write image to redis location instead of file on disk')
@click.option('--redis_key')
def real_plot(directory, filename, output_filename, write_to_redis, redis_key):
    plot(directory, filename, output_filename, write_to_redis, redis_key)

def plot(directory='', filename='aimless.log', output_filename='aimless.png', write_to_redis=False, redis_key=''):
    batch, rcp, cmposs= extract_rcp_batch(directory, filename)
    plot_rcp_batch(batch, rcp, cmposs, output_filename, write_to_redis, redis_key)
if __name__ == "__main__":
    real_plot()
