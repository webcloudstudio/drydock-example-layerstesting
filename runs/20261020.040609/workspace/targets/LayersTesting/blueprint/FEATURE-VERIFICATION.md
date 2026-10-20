# FEATURE: Acceptance Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Gate the finished ledger on the complete grader and the complete automated test suite. |
| Depends On  | ARCHITECTURE.md, FEATURE-TEST-RUNNER.md, DATABASE.md, FEATURE-DATABASE-SELECTION.md, FEATURE-AMOUNT-CENTS.md, FEATURE-LEDGER-ENTRY.md, FEATURE-CSV-OUTPUT.md, FEATURE-EXIT-CODES.md, FEATURE-USAGE-ERRORS.md, FEATURE-VALIDATE-CODE.md, FEATURE-VALIDATE-TEXT.md, FEATURE-VALIDATE-AMOUNT.md, FEATURE-VALIDATE-DATE.md, FEATURE-SCHEMA-INIT.md, FEATURE-SCHEMA-COUNT.md, FEATURE-ATOMIC-COMMANDS.md, FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-LOAD-ACCOUNTS.md, FEATURE-LOAD-CATEGORIES.md, FEATURE-LOAD-TRANSACTIONS.md, FEATURE-LOAD-ATOMIC.md, FEATURE-LOAD-HEADER.md, FEATURE-ACCOUNT-ADD.md, FEATURE-ACCOUNT-GET.md, FEATURE-ACCOUNT-RENAME.md, FEATURE-ACCOUNT-DELETE.md, FEATURE-TXN-POST.md, FEATURE-TXN-GET.md, FEATURE-TXN-AMEND.md, FEATURE-TXN-DELETE.md, FEATURE-TRANSFER.md, FEATURE-TRANSFER-REJECTION.md, FEATURE-REPORT-BALANCES.md, FEATURE-REPORT-CATEGORIES.md, FEATURE-REPORT-MONTHLY.md, FEATURE-CLI-HELP.md |
| Provides    | Terminal gate: `sh sources/run.sh` and `sh bin/test.sh` from the application root |

## Purpose

This is the terminal story. It runs after every implementation story has closed. It runs the supplied
grader unfiltered and the project's own test suite unfiltered, and requires both to exit 0.

## Behavior

- `sh sources/run.sh` runs unfiltered from the application root. Its exit status is the verdict.
  The grader creates its own fresh database and runs `./ledger init` first.
- `sh bin/test.sh` runs unfiltered from the application root. Its exit status is the verdict.
- The `ledger` executable exists at the application root and is executable before either run starts.
- Seed files under `sources/` reach the database only through `ledger load`, as the grader does.

## Programmatic Acceptance

=== AC verify-ledger-executable ===
Intent: The ledger executable exists at the application root and is executable.

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
=== END AC verify-ledger-executable ===

=== AC verify-grader-full ===
Intent: The supplied grader sh sources/run.sh runs unfiltered across sections A through Z and exits 0.
Suite: full
Requires: executable=sh; scope=test

import subprocess
import sys

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verify-grader-full ===

=== AC verify-test-suite-full ===
Intent: The application's own automated suite, bin/test.sh, runs unfiltered and exits 0.
Suite: full
Requires: executable=sh; scope=test

import subprocess
import sys

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verify-test-suite-full ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not filter, skip, or select a subset of `sources/run.sh` or `bin/test.sh` for this gate.
- Do not restate the grader's known answers, seed counts, or report totals in this story.
