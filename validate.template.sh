#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"
: "${PYENV_DIR:="${SCRIPT_DIR}/.venv"}"

if [ ! -e "${PYENV_DIR}/bin/activate" ]
then
    echo "Python virtual environment not found. Please finish setup."
    exit 1
fi

. "${PYENV_DIR}/bin/activate"

get_solution() {
    day="${1:?"A day must be specified to solve"}"
    part="${2:?"A part must be specified to solve"}"
    "./${day}/${day}${part}.py"
}

check_solution() {
    day="${1:?"A day must be specified to solve"}"
    part="${2:?"A part must be specified to solve"}"
    solution="${3:?"A solution must be specified to verify"}"
    actual="$(get_solution "${day}" "${part}")"
    if [ "${actual}" != "${solution}" ]
    then
        echo "Day ${day}, part ${part}, expected ${solution} but got ${actual}"
        exit 1
    fi
}

# check_solution "1" "a" ""
# check_solution "1" "b" ""
# check_solution "2" "a" ""
# check_solution "2" "b" ""
# check_solution "3" "a" ""
# check_solution "3" "b" ""
# check_solution "4" "a" ""
# check_solution "4" "b" ""
# check_solution "5" "a" ""
# check_solution "5" "b" ""
# check_solution "6" "a" ""
# check_solution "6" "b" ""
# check_solution "7" "a" ""
# check_solution "7" "b" ""
# check_solution "8" "a" ""
# check_solution "8" "b" ""
# check_solution "9" "a" ""
# check_solution "9" "b" ""
# check_solution "10" "a" ""
# check_solution "10" "b" ""
# check_solution "11" "a" ""
# check_solution "11" "b" ""
# check_solution "12" "a" ""
# check_solution "12" "b" ""
# check_solution "13" "a" ""
# check_solution "13" "b" ""
# check_solution "14" "a" ""
# check_solution "14" "b" ""
# check_solution "15" "a" ""
# check_solution "15" "b" ""
# check_solution "16" "a" ""
# check_solution "16" "b" ""
# check_solution "17" "a" ""
# check_solution "17" "b" ""
# check_solution "18" "a" ""
# check_solution "18" "b" ""
# check_solution "19" "a" ""
# check_solution "19" "b" ""
# check_solution "20" "a" ""
# check_solution "20" "b" ""
# check_solution "21" "a" ""
# check_solution "21" "b" ""
# check_solution "22" "a" ""
# check_solution "22" "b" ""
# check_solution "23" "a" ""
# check_solution "23" "b" ""
# check_solution "24" "a" ""
# check_solution "24" "b" ""
# check_solution "25" "a" ""
# check_solution "25" "b" ""
