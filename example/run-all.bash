#!/usr/bin/env bash
quote_arg() {
    if [[ "$1" =~ ( ) ]]; then
        echo -n "'$1' "
    else
        echo -n "$1 "
    fi
}

run_script() {
    echo
    echo -n "~~~~~  Running "
    for arg in "$@"; do
        quote_arg "${arg}"
    done
    echo " ~~~~~"
    echo
    python3 "$@"
    echo
}

ORIG_DIR=$(pwd)
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd "${SCRIPT_DIR}" || exit 1
python3 -m pip uninstall -y shell-logger
cd ..
python3 -m pip install .
cd "${SCRIPT_DIR}" || exit 1
run_script hello_world_html.py
run_script hello_world_html_and_console.py
run_script hello_world_html_with_stats.py
run_script build_flex.py
cd "${ORIG_DIR}" || exit 1
