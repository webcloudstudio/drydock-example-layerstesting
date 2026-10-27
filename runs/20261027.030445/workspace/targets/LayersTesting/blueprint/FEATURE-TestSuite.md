# FEATURE: Test Suite

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | A POSIX-compatible bin/test.sh runs the application's pytest suite against a real temporary database and exits zero only when every test passes. |
| Depends On | FEATURE-UsageErrors.md, FEATURE-LedgerCli.md |
| Provides | bin/test.sh |
| Consumes | ledger |

## Purpose

The application carries its own automated suite. `bin/test.sh` is the single entry point used by the Compass verification protocol for every behavioral story.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Behavior

1. `bin/test.sh` is POSIX sh. It changes to the application root, activates `.venv` when present, runs `pytest -q`, and exits with pytest's status.
2. The suite lives under `tests/` and runs each test against a real temporary SQLite file, selected through `DATABASE_URL` inside the test, never the shared application store.
3. Coverage: every command; every exit code 0 to 4; rules 1 to 7 (atomic rejection of loads and transfers, non-negative balances for post, amend, delete, transfer, and load, code/name/memo limits, amount formats, real calendar dates including Gregorian leap-day handling, transaction id assignment, report totals including empty-ledger totals); database path selection order; and database-open failure exiting 1.
4. The suite never reads `sources/run.sh` and embeds no report answer computed elsewhere; expected values are derived from fixture inputs written by the tests.
5. Expected values in the suite are observed against real output, since the suite is written beside the code.

## Programmatic Acceptance

=== AC testsh-present ===
Intent: bin/test.sh exists and is syntactically valid POSIX sh.
Requires: executable=sh; scope=test

import os
import subprocess

path = "bin/test.sh"
assert os.path.isfile(path)
result = subprocess.run(["sh", "-n", path], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsh-present ===

=== AC testsh-suite-files ===
Intent: The pytest suite is present and spans several test modules covering the commands.

import glob

files = glob.glob("tests/test_*.py")
print(files)
assert len(files) >= 3
=== END AC testsh-suite-files ===

=== AC testsh-passes ===
Intent: Running bin/test.sh exits zero, meaning every automated test in the suite passes.
Suite: scoped
Requires: executable=sh; scope=test

import os
import subprocess
import sys

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC testsh-passes ===

## User Acceptance

- None.

## Guardrails

- The suite uses a temporary database and never the shared application store.
- The suite never reads `sources/run.sh` or the seed files from application code.
- `bin/test.sh` exits non-zero when any test fails.
