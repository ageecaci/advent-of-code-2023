#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"
: "${PYENV_DIR:="${SCRIPT_DIR}/.venv"}"

if ! which python3 >/dev/null
then
    echo "Python not found"
    exit 1
fi

if [ ! -d "${PYENV_DIR}" ]
then
    mkdir -p "${PYENV_DIR}"
fi

if [ ! -e "${PYENV_DIR}/bin/activate" ]
then
    python3 -m venv "${PYENV_DIR}"
fi

. "${PYENV_DIR}/bin/activate"
pip install -r "${SCRIPT_DIR}/requirements.txt"
