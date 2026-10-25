# FEATURE: Release Verification

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Run the supplied grader unfiltered against the finished ledger as the terminal release check. |
| Depends On | FEATURE-TestSuite.md, FEATURE-BalanceRule.md, FEATURE-Init.md, FEATURE-Count.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-TxnPost.md, FEATURE-TxnGet.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md, FEATURE-UsageErrors.md, FEATURE-OutputContract.md, FEATURE-DatabaseResolution.md |
| Provides | release verification |
| Consumes | ledger executable, bin/test.sh |

## Purpose

The terminal story. Once every other story has closed, it runs `sh sources/run.sh` from the
application root without filtering and requires exit status zero. That exit status is the whole
verdict. The grader creates its own temporary database, so the run must not share the configured
application store.

## Behavior

- The assembled application provides an executable `ledger` at the application root.
- `sh sources/run.sh` exits zero: all 43 checks pass.
- Nothing under `sources/` is modified to obtain that result.

## Database Interface

- None — persistence is owned by FEATURE-Init.md.

## Programmatic Acceptance

=== AC release-ledger-executable ===
Intent: An executable named ledger exists at the application root.

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
=== END AC release-ledger-executable ===

=== AC release-grader-passes ===
Intent: The supplied grader exits zero when run unfiltered against the finished application.
Suite: full
Requires: executable=sh; scope=test

import os
import re
import subprocess

# The grader makes its own temporary database unless DATABASE_URL is set; keep it away from the
# configured application store.
env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "DATABASE_PATH")}
result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
    env=env,
    timeout=900,
)
print(result.stdout)
print(result.stderr)
tally = re.findall(r"(\d+) passed, (\d+) failed", result.stdout)
if tally:
    print("grader tally (passed, failed):", tally[-1])
assert result.returncode == 0
=== END AC release-grader-passes ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not filter, skip, or reinterpret any check in the grader.
- Application code never reads `sources/run.sh` or any seed file; seed files reach the database
  only through `ledger load`.
