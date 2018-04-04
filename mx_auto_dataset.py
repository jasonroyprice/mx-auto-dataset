from beamline import redis
from rq.decorators import job
from subprocess import call, Popen
import subprocess
import config
import os

@job(config.REDIS_QUEUE_NAME, connection=redis, timeout=1800)
def dataset(*args, **kwargs):
    pipeline_path = config.PIPELINE_PATH
    dir_path = os.path.dirname(os.path.realpath(pipeline_path))
    os.chdir(dir_path)
    output = Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
    version = output.stdout.read()[0:7]
    print "RUNNING %s AUTODATASET VERSION %s" % (config.PIPELINE_NAME, version)
    cmd = [pipeline_path]

    for key, value in kwargs.items():
        cmd.append("--%s" % key)
        cmd.append(str(value))

    call(cmd, cwd='/tmp')
