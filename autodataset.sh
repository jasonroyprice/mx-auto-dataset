#!/bin/bash
source /xray/progs/setups/bash/pxsetup.sh
export BEAMLINE=MX2_test
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
