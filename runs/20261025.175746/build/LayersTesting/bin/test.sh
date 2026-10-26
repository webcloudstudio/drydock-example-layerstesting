#!/bin/sh
# CommandCenter Operation
# Name: Run Test Suite
# Type: batch

# Activates .venv and runs the project test suite (pytest -q) from the application root.
# Exits 0 only when every test passes.
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
LOG_FILE="$LOG_DIR/test_${TIMESTAMP}.log"

echo "=== test started at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Arguments: $*" | tee -a "$LOG_FILE"
echo "Working dir: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

if [ ! -f ".venv/bin/activate" ]; then
    echo "error: .venv is missing; run 'uv venv .venv' and 'uv sync' first." | tee -a "$LOG_FILE" >&2
    exit 1
fi

# POSIX sh has no pipefail, so capture pytest's own status instead of piping through tee.
# The activate script reads unset variables, so nounset is relaxed only around it.
set +eu
. .venv/bin/activate
set -u
pytest -q "$@" > "$LOG_FILE.pytest" 2>&1
STATUS=$?
set -e
cat "$LOG_FILE.pytest" | tee -a "$LOG_FILE"
rm -f "$LOG_FILE.pytest"

echo "=== test finished at $(date '+%Y-%m-%d %H:%M:%S') with status $STATUS ===" | tee -a "$LOG_FILE"
exit "$STATUS"
