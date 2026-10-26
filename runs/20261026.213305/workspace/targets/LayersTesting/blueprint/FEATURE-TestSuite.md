# FEATURE: Test Suite

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The POSIX `bin/test.sh` entry point and the application's own pytest suite covering every command, exit code and rule. |
| Depends On | FEATURE-CliUsage.md, FEATURE-LedgerInit.md, FEATURE-LedgerCount.md, FEATURE-LoadTransactions.md, FEATURE-AccountDelete.md, FEATURE-AccountRename.md, FEATURE-TxnGet.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides | bin/test.sh |
| Consumes | ledger |

## Purpose

The application ships its own automated tests. `sh bin/test.sh` runs them from the application root and exits zero only when every test passes.

## Behavior

- `bin/test.sh` is POSIX `sh`. It changes to the application root, activates `.venv` when present, and runs `pytest -q`, exiting with pytest's exit status.
- Tests live under `tests/` and cover each command, each exit code (0, 1, 2, 3, 4) and each rule: all-or-nothing loads and transfers, non-negative balances judged on the final state, amount and date validation, id assignment, and report output.
- Every test creates its own temporary SQLite database and removes it afterwards, by setting `DATABASE_URL` to a path under a temporary directory. No test opens or modifies `data/app.db`.
- Tests obtain seed data only by invoking `ledger load` on files under `sources/`; application code never reads them.
- Tests reach the database only through the persistence package.

## Programmatic Acceptance

=== AC test-suite-script-shape ===
Intent: bin/test.sh exists, parses as POSIX sh, and the suite has test modules.

Requires: executable=sh; scope=test

import glob
import os
import subprocess

assert os.path.isfile("bin/test.sh")
result = subprocess.run(["sh", "-n", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
modules = glob.glob("tests/test_*.py")
print(modules)
assert len(modules) > 0
=== END AC test-suite-script-shape ===

=== AC test-suite-passes ===
Intent: Running the application's own suite through bin/test.sh succeeds.

Requires: executable=sh; scope=test

import subprocess

result = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC test-suite-passes ===

## User Acceptance

- None.

## Guardrails

- No test touches `data/app.db`.
- Each test creates and removes its own temporary database.
- Seed files reach the database only through `ledger load`, never from application code.
- `bin/test.sh` exits zero only when every test passes.
