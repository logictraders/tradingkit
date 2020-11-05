#!/usr/bin/env bash
set -e

if ! test -f /venv/bin/python;then
    python3 -m venv /venv
    source /venv/bin/activate
    pip install -e .
else
    source /venv/bin/activate
fi

exec "$@"

