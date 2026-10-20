# FEATURE: Acceptance Grader

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Stages the supplied `sources/run.sh` grader and seed files into the application root and gates on the grader passing end to end. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CLI-Platform.md, FEATURE-Database-Location.md, FEATURE-Operational-Errors.md, FEATURE-Command-Transaction.md, FEATURE-Schema-Init.md, FEATURE-Schema-Count.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Code-Validation.md, FEATURE-Amount-Format.md, FEATURE-Date-Validation.md, FEATURE-CLI-Help.md, FEATURE-Balance-Rule.md, FEATURE-Load-Accounts.md, FEATURE-Load-Categories.md, FEATURE-Load-Transactions.md, FEATURE-Account-Add.md, FEATURE-Account-Get.md, FEATURE-Account-Rename.md, FEATURE-Account-Delete.md, FEATURE-Transaction-Post.md, FEATURE-Transaction-Get.md, FEATURE-Transaction-Amend.md, FEATURE-Transaction-Delete.md, FEATURE-Transfer.md, FEATURE-Report-Balances.md, FEATURE-Report-Categories.md, FEATURE-Report-Monthly.md, FEATURE-Automated-Suite.md |
| Provides    | `sh sources/run.sh` exits 0 |
| Consumes    | ./ledger, sources/run.sh, sources/seed_accounts.csv, sources/seed_categories.csv, sources/seed_transactions.csv, sources/seed_transactions_bad.csv |

## Purpose

This is the terminal verification story. It runs last, after every other story closes. It stages the supplied grader and its seed files verbatim into the application root, then runs the grader unfiltered from the application root.

The grader is the acceptance verdict for the project. Its exit status decides this story.

## Behavior

- Stage `sources/run.sh` and `sources/seed_accounts.csv`, `sources/seed_categories.csv`, `sources/seed_transactions.csv`, and `sources/seed_transactions_bad.csv` into `sources/` under the application root, byte for byte. Do not author, rewrite, trim, or regenerate them.
- Run `sh sources/run.sh` unfiltered from the application root.
- The story passes only when that run exits 0.

## Programmatic Acceptance

=== AC grader-staged-executable ===
Intent: The ledger executable exists at the application root and is executable before the grader runs.
Requires: executable=sh; scope=test

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
=== END AC grader-staged-executable ===

=== AC grader-full ===
Intent: The supplied grader sh sources/run.sh exits 0 unmodified against the completed application, running every check it contains.
Suite: full
Requires: executable=sh; scope=test

import os
import subprocess
import sys

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True, text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC grader-full ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute `sources/run.sh` or any seed file.
- Application code must never read `sources/run.sh` or any seed file. Seed files reach the database only through `ledger load`.
- Do not hardcode a report row, count, or total to make the grader pass.
