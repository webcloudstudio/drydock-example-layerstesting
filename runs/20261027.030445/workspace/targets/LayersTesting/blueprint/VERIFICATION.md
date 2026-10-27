# FEATURE: Verification

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Terminal release gate: the finished ledger passes every check in the supplied grader and the application suite. |
| Depends On | FEATURE-TestSuite.md, FEATURE-UsageErrors.md, FEATURE-ReportMonthly.md, FEATURE-Transfer.md |
| Provides | verification |
| Consumes | ledger, bin/test.sh |

## Purpose

This assembly story confirms the integrated product. It runs the supplied grader unfiltered and the application's own suite. It adds no behavior.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Behavior

1. `ledger` exists at the application root and is executable.
2. `sh bin/test.sh` exits zero.
3. `sh sources/run.sh` exits zero with all 43 checks passing.
4. No file under `sources/` is modified.

## Programmatic Acceptance

=== AC verify-ledger-executable ===
Intent: The deliverable is an executable file named ledger at the application root.

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
=== END AC verify-ledger-executable ===

=== AC verify-application-suite ===
Intent: The application's own automated suite passes through bin/test.sh.
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
=== END AC verify-application-suite ===

=== AC verify-supplied-grader ===
Intent: The supplied grader passes every check; its exit status is the whole verdict. The child environment omits DATABASE_URL so the grader uses its own fresh temporary database.
Suite: full
Requires: executable=sh; scope=test

import os
import subprocess
import sys

env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
    env=env,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verify-supplied-grader ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Application code never reads `sources/run.sh` or any seed file.
- No report row, count, or total is hardcoded; every value comes from a query.
