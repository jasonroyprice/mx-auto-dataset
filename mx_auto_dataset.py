from beamline import redis
from rq.decorators import job
from subprocess import call
import config

@job(config.REDIS_QUEUE_NAME, connection=redis, timeout=1800)
def dataset(*args, **kwargs):
    print "RUNNING %s AUTODATASET" % config.PIPELINE_NAME
    cmd = ['/xray/progs/Python/libraries/mx_auto_dataset_cpu3/autodataset.sh']

    for key, value in kwargs.iteritems():
        cmd.append("--%s" % key)
        cmd.append(str(value))

    call(cmd, cwd='/tmp')
