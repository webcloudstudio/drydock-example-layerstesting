# FEATURE: Report Monthly

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `ledger report monthly` writes one row per month that has transactions, plus a TOTAL row, computed from the database. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-LoadTransactions.md, FEATURE-TxnPost.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md |
| Provides    | ledger report monthly |
| Consumes    | transactions.list |

## Purpose

Report totals per calendar month. Months with no transactions do not appear.

## Trigger

`ledger report monthly` with no further arguments.

## Behavior

- Read every transaction through `transactions.list`.
- Group transactions by the `YYYY-MM` prefix of `date`.
- For each month with at least one transaction, compute `transactions` (count), `inflow` (sum of
  positive amounts), `outflow` (sum of absolute values of negative amounts, written positive), and
  `net` (`inflow - outflow`).
- Write the header `month,transactions,inflow,outflow,net`, then one row per month in ascending
  order.
- Write `TOTAL,<count>,<inflow>,<outflow>,<net>` as the final row, summed over all transactions.
- Amounts use exactly two decimals, a leading `-` when negative, and no thousands separator.
- With no transactions, write the header and `TOTAL,0,0.00,0.00,0.00` with no month rows.
- Exit 0 on success.
- A database that cannot be read exits 1 with nothing on standard output.

## Output

```text
month,transactions,inflow,outflow,net
2026-01,40,9659.45,5215.00,4444.45
...
TOTAL,120,19878.95,15645.00,4233.95
```

## Programmatic Acceptance

=== AC RPT-003-empty-monthly ===
Intent: On an empty transactions table, report monthly writes the header and TOTAL,0,0.00,0.00,0.00 with no month rows.
Suite: scoped
Requires: executable=python3; scope=test

import subprocess
import sys

from persistence.testing import db_session

with db_session() as db:
    expected_header = "month,transactions,inflow,outflow,net"
    expected_total = "TOTAL,0,0.00,0.00,0.00"
    result = subprocess.run(
        [sys.executable, "-m", "cli", "report", "monthly"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    lines = [line for line in result.stdout.splitlines() if line]
    assert result.returncode == 0
    assert lines[0] == expected_header
    assert lines[-1] == expected_total
    assert len(lines) == 2
=== END AC RPT-003-empty-monthly ===

=== AC RPT-003-months-ascending ===
Intent: Month rows appear in ascending YYYY-MM order, one per month that has transactions.
Suite: scoped
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="SAFE", name="Store Safe")
    db.categories.create(category="SALES", description="Sales receipts")
    db.transactions.create(txn_id=1, date="2026-02-01", account="SAFE", category="SALES", amount=500, memo="")
    db.transactions.create(txn_id=2, date="2026-01-01", account="SAFE", category="SALES", amount=500, memo="")
    code, out, err = cli_runner("report", "monthly")
    rows = [line for line in out.splitlines() if line]
    assert code == 0
    assert rows[1].split(",")[0] == "2026-01"
    assert rows[2].split(",")[0] == "2026-02"
    assert rows[-1].startswith("TOTAL,")
=== END AC RPT-003-months-ascending ===

## User Acceptance

- None.

## Guardrails

- Month rows are derived from transaction dates; no month is hardcoded.
- Application code does not read `sources/run.sh` or any seed file.
