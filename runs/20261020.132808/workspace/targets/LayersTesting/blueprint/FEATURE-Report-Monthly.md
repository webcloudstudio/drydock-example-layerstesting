# Feature: Report Monthly

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one row per calendar month that has transactions, ascending, then a TOTAL row, all computed from the database. |
| Depends On  | DATABASE.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger report monthly |
| Consumes    | transactions.list |

## Purpose

`ledger report monthly` reports, for each month that has transactions, its transaction count,
inflow, outflow, and net, followed by a TOTAL row.

## Trigger

The user runs `ledger report monthly`.

## Behavior

1. Within the command transaction, read every transaction through `transactions.list`.
2. Group rows by month, the `YYYY-MM` prefix of `date`. Only months that have transactions appear.
3. For each month, compute by query:
   - `transactions`: the number of rows in that month.
   - `inflow`: the sum of positive amounts, in integer cents.
   - `outflow`: the sum of the absolute values of negative amounts, in integer cents, printed as a
     positive number.
   - `net`: `inflow - outflow`.
4. Print the header, then one row per month in ascending `YYYY-MM` order:

```text
month,transactions,inflow,outflow,net
```

5. Print the TOTAL row, whose count, inflow, outflow, and net are summed over every transaction:

```text
TOTAL,<count>,<inflow>,<outflow>,<net>
```

6. With no transactions, print only `TOTAL,0,0.00,0.00,0.00` after the header.

Amounts are formatted per FEATURE-Amount-Format.md. No value is embedded as a constant.

## Routes and Interfaces

| Interface | Kind | Notes |
|---|---|---|
| `ledger report monthly` | CLI command | Exit 0 on success. |

## Reads and Writes

| Operation | Access | Repository operation | Notes |
|---|---|---|---|
| List transactions | read | `transactions.list` | Grouped by month and totalled in code from the query result. |

## Programmatic Acceptance

=== AC report-monthly-header ===
Intent: The monthly report begins with the month header line.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("report", "monthly")
    assert code == 0
    assert out.splitlines()[0] == "month,transactions,inflow,outflow,net"
=== END AC report-monthly-header ===

=== AC report-monthly-empty ===
Intent: With no transactions the report prints only the TOTAL row of zeros.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("report", "monthly")
    assert code == 0
    assert out.splitlines()[1:] == ["TOTAL,0,0.00,0.00,0.00"]
=== END AC report-monthly-empty ===

=== AC report-monthly-month-rows ===
Intent: Each month row carries its count, inflow, outflow, and net for transactions dated in that month.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RMA1", name="Monthly Account")
    db.categories.create(category="RMC1", description="Monthly Category")
    db.transactions.create(txn_id=7401, date="2026-03-05", account="RMA1",
                           category="RMC1", amount=900, memo="in")
    db.transactions.create(txn_id=7402, date="2026-03-09", account="RMA1",
                           category="RMC1", amount=-300, memo="out")
    code, out, err = cli_runner("report", "monthly")
    assert code == 0
    rows = out.splitlines()
    assert rows[1] == "2026-03,2,9.00,3.00,6.00"
=== END AC report-monthly-month-rows ===

=== AC report-monthly-ascending ===
Intent: Month rows are ordered by YYYY-MM ascending.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RMB1", name="Monthly Order Account")
    db.categories.create(category="RMD1", description="Monthly Order Category")
    db.transactions.create(txn_id=7501, date="2026-06-01", account="RMB1",
                           category="RMD1", amount=100, memo="june")
    db.transactions.create(txn_id=7502, date="2026-04-01", account="RMB1",
                           category="RMD1", amount=100, memo="april")
    code, out, err = cli_runner("report", "monthly")
    assert code == 0
    rows = out.splitlines()
    assert rows[1].startswith("2026-04,")
    assert rows[2].startswith("2026-06,")
=== END AC report-monthly-ascending ===

=== AC report-monthly-total-row ===
Intent: The TOTAL row sums transaction count, inflow, outflow, and net over every month.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RMT1", name="Monthly Total Account")
    db.categories.create(category="RMT2", description="Monthly Total Category")
    db.transactions.create(txn_id=7601, date="2026-01-15", account="RMT1",
                           category="RMT2", amount=400, memo="jan")
    db.transactions.create(txn_id=7602, date="2026-02-15", account="RMT1",
                           category="RMT2", amount=-150, memo="feb")
    code, out, err = cli_runner("report", "monthly")
    assert code == 0
    assert out.splitlines()[-1] == "TOTAL,2,4.00,1.50,2.50"
=== END AC report-monthly-total-row ===

## User Acceptance

- None.

## Guardrails

- Only months that contain transactions appear as rows.
- No count, sum, or total is hardcoded; every value comes from a query.
- Amounts are formatted with two decimals, never floating point; a zero total prints `0.00`,
  never `-0.00`.
