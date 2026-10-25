# FEATURE: Test Suite

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Provide a POSIX bin/test.sh that runs the application's own pytest suite and exits zero only when every test passes. |
| Depends On | FEATURE-LoadRejection.md, FEATURE-AccountDelete.md, FEATURE-AccountRename.md, FEATURE-AccountDuplicate.md, FEATURE-TxnValidate.md, FEATURE-TxnDelete.md, FEATURE-TxnAmend.md, FEATURE-TransferOverdraw.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md, FEATURE-UsageErrors.md, FEATURE-OutputContract.md, FEATURE-DatabaseResolution.md, FEATURE-BalanceRule.md |
| Provides | bin/test.sh |
| Consumes | cli.main, cli.testing.cli_runner, persistence.testing.db_session |

## Purpose

`bin/test.sh` is the project's own regression gate. It runs from the application root, activates
the `.venv` environment, and runs `pytest -q`, propagating pytest's exit status.

## Behavior

- Written in POSIX `sh`; no bashisms.
- Changes to the application root regardless of the caller's working directory.
- Exits zero only when every test passes; any failure or collection error is non-zero.
- The pytest suite lives under `tests/` and covers each command, each exit code (`0` to `4`), and
  each rule in the instructions: rejected commands change nothing, no negative balances, code, name,
  memo, amount, and date validation, transaction id assignment, transfer pairing, and the three
  reports. Each test runs against its own temporary database; none uses `sources/run.sh`.
- No test invokes `bin/test.sh` itself.

## Database Interface

- None — persistence is owned by FEATURE-Init.md.

## Programmatic Acceptance

=== AC testsh-exists-and-parses ===
Intent: bin/test.sh exists and is valid POSIX sh syntax.
Requires: executable=sh; scope=test

import os
import subprocess

assert os.path.isfile("bin/test.sh")
result = subprocess.run(["sh", "-n", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsh-exists-and-parses ===

=== AC testsh-suite-is-collected ===
Intent: pytest collects at least one test from the application's suite.

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--collect-only", "-q"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsh-suite-is-collected ===

=== AC testsh-passes ===
Intent: Running sh bin/test.sh from the application root exits zero.
Requires: executable=sh; scope=test

import subprocess

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
    timeout=900,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsh-passes ===

=== AC testsh-works-from-other-directory ===
Intent: bin/test.sh finds the application root when launched from a different working directory.
Requires: executable=sh; scope=test

import os
import subprocess
import tempfile

script = os.path.abspath("bin/test.sh")
with tempfile.TemporaryDirectory() as elsewhere:
    result = subprocess.run(
        ["sh", script],
        capture_output=True,
        text=True,
        cwd=elsewhere,
        timeout=900,
    )
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsh-works-from-other-directory ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` never reads or runs `sources/run.sh`.
- Tests never use the configured application store; each creates a temporary database.
- Tests use no network access other than a PostgreSQL server named by `DATABASE_URL`.
