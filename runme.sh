#!/usr/bin/env bash
# If invoked via `sh runme.sh`, re-exec with bash to guarantee bash syntax support.
if [ -z "${BASH_VERSION:-}" ]; then
    exec /usr/bin/env bash "$0" "$@"
fi

set -euo pipefail

################################################################################
# Script to handle python environment and startup given script
################################################################################

################################################################################
# Set base variables, you may tweak here
################################################################################
# Set name of python environment
ENV_NAME=".venv"
# Set name of python environment list exported by pip freeze > ${REQ_NAME}
REQ_NAME="requirements.txt"
# Get name of script to start
SCRIPT="${1:-}"
# Set default name of script to run
DEF_SCRIPT="program.py"

################################################################################
# Set internal variables, don't touch unless you know what you're doing!
################################################################################
# Get startup path of script
PATH_BASE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# Set FQN of environment
PATH_ENVIRONMENT="${PATH_BASE}/${ENV_NAME}"
# Set interpreter inside virtual environment
PY_VENV="${PATH_ENVIRONMENT}/bin/python"

# Determine system python interpreter for creating venv
PY_BOOTSTRAP=python3
if ! command -v "${PY_BOOTSTRAP}" >/dev/null 2>&1; then
    PY_BOOTSTRAP=python
fi
if ! command -v "${PY_BOOTSTRAP}" >/dev/null 2>&1; then
    echo "Cannot find a Python interpreter, abort"
    exit 1
fi

################################################################################
# Check environment for existence
################################################################################
if [[ ! -d "${PATH_ENVIRONMENT}" ]]; then
    # Create environment
    echo "Create missing environment [${ENV_NAME}]"
    "${PY_BOOTSTRAP}" -m venv "${PATH_ENVIRONMENT}"

    # Install required modules
    if [[ -f "${PATH_BASE}/${REQ_NAME}" ]]; then
        echo "Install required modules from [${REQ_NAME}]"
        "${PY_VENV}" -m pip install -r "${PATH_BASE}/${REQ_NAME}"
    else
        echo "List of required modules [${REQ_NAME}] not found"
    fi
fi

################################################################################
# Ensure virtual environment python exists
################################################################################
if [[ ! -x "${PY_VENV}" ]]; then
    echo "Python interpreter in environment [${ENV_NAME}] not found, abort"
    exit 1
fi

################################################################################
# Handle special commands or determine script to run
################################################################################
if [[ "${SCRIPT}" == "tests" ]]; then
    echo "Execute tests"
    "${PY_VENV}" -m unittest discover -s tests -p "test_*.py"
else
    # If no name is passed, use default
    if [[ -z "${SCRIPT}" ]]; then
        SCRIPT="${DEF_SCRIPT}"
    fi

    SCRIPT_PATH="${PATH_BASE}/${SCRIPT}"

    ################################################################################
    # Execute script
    ################################################################################
    if [[ -f "${SCRIPT_PATH}" ]]; then
        echo "Execute script [${SCRIPT}]"
        "${PY_VENV}" "${SCRIPT_PATH}"
    else
        echo "Script [${SCRIPT}] not found :-("
        exit 1
    fi
fi
