#!/bin/sh
# CommandCenter Operation
# Name: Run Test Suite
# Type: batch

# --- Standard Preamble ---
set -eu
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
SCRIPT_NAME=$(basename "$0" .sh)
LOG_FILE="$LOG_DIR/${SCRIPT_NAME}_${TIMESTAMP}.log"

echo "=== $SCRIPT_NAME started at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Arguments: $*" | tee -a "$LOG_FILE"
echo "Working dir: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

if [ ! -f .venv/bin/activate ]; then
    echo "error: no environment at $PROJECT_DIR/.venv; run: uv sync" | tee -a "$LOG_FILE" >&2
    exit 1
fi

# activate reads unset variables, so relax -u only while sourcing it.
set +u
. .venv/bin/activate
set -u
# Capture the test exit status directly; a pipe to tee would hide it under POSIX sh.
set +e
pytest -q "$@" > "$LOG_FILE.pytest" 2>&1
STATUS=$?
set -e
cat "$LOG_FILE.pytest" | tee -a "$LOG_FILE"
rm -f "$LOG_FILE.pytest"

echo "=== $SCRIPT_NAME finished at $(date '+%Y-%m-%d %H:%M:%S') with exit $STATUS ===" | tee -a "$LOG_FILE"
exit "$STATUS"
