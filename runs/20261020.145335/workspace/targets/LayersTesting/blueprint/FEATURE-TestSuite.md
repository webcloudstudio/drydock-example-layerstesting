# FEATURE: Test Suite

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `bin/test.sh` runs the application's pytest suite from the application root against a temporary database and exits zero only when every test passes. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-DatabaseTarget.md, FEATURE-CommandTransaction.md, FEATURE-InitSchema.md, FEATURE-CountRows.md, FEATURE-ValidateText.md, FEATURE-ValidateAmount.md, FEATURE-ValidateDate.md, FEATURE-NonNegativeBalance.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-AccountDelete.md, FEATURE-TxnPost.md, FEATURE-TxnGet.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides    | bin/test.sh |
| Consumes    | ledger executable, pytest |

## Purpose

Provide the POSIX runner for the application's own pytest suite, so the suite can be executed from
a single command with a single exit status.

## Trigger

`sh bin/test.sh` from the application root.

## Behavior

- Create a temporary database location and point `DATABASE_URL` at it for the run.
- Run `pytest -q` from the application root.
- Exit with the pytest exit status: zero only when every test passes.
- Remove the temporary database location on exit.
- Write nothing to standard output other than pytest's own output.

## Output

Pytest's output. The exit status is the verdict.

## Programmatic Acceptance

=== AC VERIFY-001-runner-exit-status ===
Intent: bin/test.sh runs the pytest suite and exits zero only when every test passes.
Suite: scoped
Requires: executable=sh; scope=test
Requires: executable=python3; scope=test

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
=== END AC VERIFY-001-runner-exit-status ===

=== AC VERIFY-001-temporary-database ===
Intent: bin/test.sh points the suite at a temporary database, not the project's data/app.db.
Suite: scoped
Requires: executable=sh; scope=test
Requires: executable=python3; scope=test

import os
import subprocess
import sys
from pathlib import Path

default_db = Path("data/app.db")
before = default_db.stat().st_mtime if default_db.exists() else None
result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
after = default_db.stat().st_mtime if default_db.exists() else None
assert result.returncode == 0
assert before == after
=== END AC VERIFY-001-temporary-database ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` is POSIX `sh`; it does not depend on bash.
- The runner does not modify `sources/`, `COMPASS.md`, or any seed file.
