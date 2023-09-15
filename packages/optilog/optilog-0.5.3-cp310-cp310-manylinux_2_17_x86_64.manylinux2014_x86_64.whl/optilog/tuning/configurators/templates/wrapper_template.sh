#!/usr/bin/env bash

ulimit -c 0  # Do not generate core files

CWD="$(realpath "$(dirname "${0}")")"         # Path to the wrapper directory
WRAPPER_PY="${CWD}/python_entrypoint.py" # Path to wrapper_template.py
EXECUTION_TYPE="wrapper-args"
PYTHON_EXEC="__@PYTHON#@PATH#__"

exec "$PYTHON_EXEC" "${WRAPPER_PY}" "${EXECUTION_TYPE}" ${@}