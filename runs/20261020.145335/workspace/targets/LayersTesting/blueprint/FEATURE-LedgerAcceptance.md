# FEATURE: Ledger Acceptance

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | The finished ledger passes the complete supplied grader `sh sources/run.sh` with all 43 checks. |
| Depends On  | FEATURE-TestSuite.md, ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-DatabaseTarget.md, FEATURE-InitSchema.md, FEATURE-CountRows.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-AccountDelete.md, FEATURE-TxnPost.md, FEATURE-TxnGet.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-NonNegativeBalance.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides    | end-to-end grader pass |
| Consumes    | ledger executable, sources/run.sh |

## Purpose

Terminal acceptance. Assembles the finished ledger and gates on the supplied grader, which is the
sole verdict for project correctness.

## Trigger

`sh sources/run.sh` from the application root, run after every other story has closed.

## Behavior

- The grader creates a fresh database, runs `ledger init`, loads the three seed files, and runs its
  fixed sequence of 43 checks.
- Each check compares one command's exit code and standard output with the known answer.
- The grader exits zero only when every check passes.

## Output

```text
LayersTesting: 43 passed, 0 failed (of 43)
```

## Programmatic Acceptance

=== AC VERIFY-002-full-grader ===
Intent: The complete supplied grader exits zero with every check passing.
Suite: full
Requires: executable=sh; scope=test

import os
import subprocess
import sys

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
    env={**os.environ},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC VERIFY-002-full-grader ===

## User Acceptance

- None.

## Guardrails

- `sources/run.sh` is run as supplied; it is not modified, filtered, or reinterpreted.
- No check invokes the grader in a list or dry-run mode.
