#!/bin/bash
source /xray/progs/setups/bash/pxsetup.sh
export PATH=/beamline/apps/python/2.7.13/bin:$PATH
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
