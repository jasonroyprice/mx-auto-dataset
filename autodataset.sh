#!/bin/bash
source /beamline/other/setup/pxsetup.sh
exec $(dirname $(readlink -f $0))/autodataset.py "$@"
