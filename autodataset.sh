#!/bin/bash
source /xray/progs/setups/bash/pxsetup.sh
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
