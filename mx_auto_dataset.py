from beamline import redis
from rq.decorators import job
from subprocess import call

@job('autodatasetdev', connection=redis, timeout=1800)
def dataset(*args, **kwargs):
    print "RUNNING NEW AUTODATASET"
    cmd = ['/beamline/apps/mx-auto-dataset/autodataset.sh']

    for key, value in kwargs.iteritems():
        cmd.append("--%s" % key)
        cmd.append(str(value))

    call(cmd, cwd='/scratch')
