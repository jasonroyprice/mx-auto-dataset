from beamline import redis
from rq.decorators import job
from subprocess import call

@job('default', connection=redis, timeout=1800)
def dataset(*args, **kwargs):
    print "RUNNING NEW AUTODATASET"
    cmd = ['/xray/progs/Python/applications/autodataset/new/autodataset.sh']

    for key, value in kwargs.iteritems():
        cmd.append("--%s" % key)
        cmd.append(str(value))

    call(cmd, cwd='/ssd/test')