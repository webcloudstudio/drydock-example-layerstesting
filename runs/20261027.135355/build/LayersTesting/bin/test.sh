#!/bin/sh
# CommandCenter Operation
# Name: Run Test Suite
# Type: batch

# --- Standard Preamble (POSIX sh) ---
set -eu
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
LOG_FILE="$LOG_DIR/test_${TIMESTAMP}.log"
STATUS_FILE="$LOG_DIR/test_${TIMESTAMP}.status"

echo "=== test started at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Arguments: $*" | tee -a "$LOG_FILE"
echo "Working dir: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

# Create the environment from the committed lock when it is missing.
if [ ! -f .venv/bin/activate ]; then
    uv sync --locked 2>&1 | tee -a "$LOG_FILE"
fi

# The pytest exit status is the verdict; tee would hide it, so record it to a file.
# shellcheck disable=SC1091
( set +u; . .venv/bin/activate; set -u; pytest -q "$@"; echo $? > "$STATUS_FILE" ) 2>&1 | tee -a "$LOG_FILE"
status=$(cat "$STATUS_FILE")
rm -f "$STATUS_FILE"

echo "=== test finished at $(date '+%Y-%m-%d %H:%M:%S') with exit $status ===" | tee -a "$LOG_FILE"
exit "$status"
