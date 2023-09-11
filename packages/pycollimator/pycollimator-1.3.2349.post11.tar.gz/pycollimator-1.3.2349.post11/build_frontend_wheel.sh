#!/bin/bash

set -eu

GITDIR=${GITDIR:-`git rev-parse --show-toplevel`}
source "${GITDIR}/src/scripts/common.sh"
cd `dirname $0`

do_echo "Building pycollimator wheel for the frontend..."

# Installing build only if necessary. On Arch, pip install --user may complain and fail.
if ! python3 -m build --version ; then
    do_exec python3 -m pip install --user build
fi

do_exec rm -rf pycollimator.egg-info dist
do_exec python3 -m build

WHL=`ls -rt ../../lib/pycollimator/dist/*.whl | head -n1`
do_exec mkdir -p "$GITDIR/src/services/frontend/public/wheels"
do_exec cp -f "$WHL" "$GITDIR/src/services/frontend/public/wheels/pycollimator-0.0.1-py3-none-any.whl"
