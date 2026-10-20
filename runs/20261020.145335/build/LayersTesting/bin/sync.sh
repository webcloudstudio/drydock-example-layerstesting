#!/bin/sh
# LayersTesting Operation
# Name: Sync environment
# Type: batch

# Creates .venv if needed and installs the locked dependency set from uv.lock.
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_DIR"

if [ ! -d .venv ]; then
    uv venv .venv
fi

uv sync --locked
