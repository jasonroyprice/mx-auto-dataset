#!/bin/bash
source /xray/progs/setups/bash/pxsetup.sh
export PATH=/home/user3id1/bin:$PATH
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
