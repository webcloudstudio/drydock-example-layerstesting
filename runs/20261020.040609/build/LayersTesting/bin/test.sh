#!/bin/sh
# CommandCenter Operation
# Name: Run Test Suite
# Type: batch
#
# Runs `pytest -q` from the application root against a fresh temporary database.
#
#   sh bin/test.sh          run the whole suite
#   sh bin/test.sh SLICE    run only the tests matching SLICE (pytest -k expression)
#
# Exit status is pytest's: 0 only when every selected test passes.
set -u

APP=$(cd "$(dirname "$0")/.." && pwd)
cd "$APP" || exit 1

WORK=$(mktemp -d) || exit 1
trap 'rm -rf "$WORK"' EXIT INT TERM

# Never point the suite at the user's database: always a fresh temporary SQLite file.
DATABASE_URL=$WORK/test.db
export DATABASE_URL

if [ -x "$APP/.venv/bin/python" ]; then
    PYTHON=$APP/.venv/bin/python
else
    PYTHON=python3
fi

rc=0
if [ $# -ge 1 ]; then
    "$PYTHON" -m pytest -q -k "$1" || rc=$?
else
    "$PYTHON" -m pytest -q || rc=$?
fi
exit "$rc"
