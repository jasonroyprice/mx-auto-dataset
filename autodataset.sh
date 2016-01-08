#!/bin/bash
source /beamline/other/setup/pxsetup.sh
export PATH=/beamline/xdsme-v0.5.0.9/bin/Linux_i586:${PATH}
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
