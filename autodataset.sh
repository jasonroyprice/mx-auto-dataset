#!/bin/bash
source /xray/progs/setups/bash/pxsetup.sh
export PATH=/forkintegrate/bin:$PATH
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
