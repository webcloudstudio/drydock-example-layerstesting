#!/bin/sh
# LayersTesting Operation
# Name: Run test suite
# Type: batch

# Activates the project environment and runs the declared test command (pytest -q).
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_DIR"

if [ ! -f .venv/bin/activate ]; then
    echo "error: .venv is missing; run sh bin/sync.sh first." >&2
    exit 1
fi

set +u
. .venv/bin/activate
set -u
exec pytest -q "$@"
