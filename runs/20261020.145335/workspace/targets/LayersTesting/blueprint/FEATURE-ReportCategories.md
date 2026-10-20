# FEATURE: Report Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | `ledger report categories` writes every category with inflow, outflow, and net, plus a TOTAL row, computed from the database. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliDispatch.md, FEATURE-CliOutput.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-TxnPost.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md |
| Provides    | ledger report categories |
| Consumes    | categories.list, transactions.list |

## Purpose

Report totals for every category. Categories with no transactions still appear.

## Trigger

`ledger report categories` with no further arguments.

## Behavior

- Read every category through `categories.list`, ordered by `category` ascending.
- For each category, compute from `transactions.list`: `transactions` (count), `inflow` (sum of
  positive amounts), `outflow` (sum of absolute values of negative amounts, written positive), and
  `net` (`inflow - outflow`).
- Write the header `category,description,transactions,inflow,outflow,net`, then one row per
  category in code order, including categories with zero transactions.
- Write `TOTAL,,<count>,<inflow>,<outflow>,<net>` as the final row, summed over all transactions.
- Amounts use exactly two decimals, a leading `-` when negative, and no thousands separator.
- With no categories and no transactions, write the header and `TOTAL,,0,0.00,0.00,0.00`.
- Exit 0 on success.
- A database that cannot be read exits 1 with nothing on standard output.

## Output

```text
category,description,transactions,inflow,outflow,net
OPENING,Opening balance,2,5200.00,0.00,5200.00
...
TOTAL,,120,19878.95,15645.00,4233.95
```

## Programmatic Acceptance

=== AC RPT-002-empty-categories ===
Intent: On empty tables, report categories writes the header and TOTAL,,0,0.00,0.00,0.00.
Suite: scoped
Requires: executable=python3; scope=test

import subprocess
import sys

from persistence.testing import db_session

with db_session() as db:
    expected_header = "category,description,transactions,inflow,outflow,net"
    expected_total = "TOTAL,,0,0.00,0.00,0.00"
    result = subprocess.run(
        [sys.executable, "-m", "cli", "report", "categories"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    lines = [line for line in result.stdout.splitlines() if line]
    assert result.returncode == 0
    assert lines[0] == expected_header
    assert lines[-1] == expected_total
=== END AC RPT-002-empty-categories ===

=== AC RPT-002-zero-transaction-categories-listed ===
Intent: A category with no transactions still appears in the report, with zero counts.
Suite: scoped
Requires: executable=python3; scope=test

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.categories.create(category="RENT", description="Rent")
    code, out, err = cli_runner("report", "categories")
    rows = [line for line in out.splitlines() if line]
    assert code == 0
    assert rows[1].split(",")[0] == "RENT"
    assert rows[1].split(",")[2] == "0"
    assert rows[-1].startswith("TOTAL,,")
=== END AC RPT-002-zero-transaction-categories-listed ===

## User Acceptance

- None.

## Guardrails

- Each category's values are computed by a query; no total is hardcoded.
- Application code does not read `sources/run.sh` or any seed file.
