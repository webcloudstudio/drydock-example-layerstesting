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

# --- Activate the project environment and run the declared test command ---
if [ ! -x ".venv/bin/pytest" ]; then
    echo "error: .venv is missing; run 'uv sync' first." | tee -a "$LOG_FILE" >&2
    exit 1
fi
export VIRTUAL_ENV="$PROJECT_DIR/.venv"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

# Capture the exit status without letting tee hide it.
set +e
pytest -q "$@" > "$LOG_FILE.run" 2>&1
STATUS=$?
set -e
cat "$LOG_FILE.run" | tee -a "$LOG_FILE"
rm -f "$LOG_FILE.run"

echo "=== $SCRIPT_NAME finished at $(date '+%Y-%m-%d %H:%M:%S') with status $STATUS ===" | tee -a "$LOG_FILE"
exit "$STATUS"
