# Feature: Report Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one row per category, including categories with no transactions, ordered by code, then a TOTAL row, all computed from the database. |
| Depends On  | DATABASE.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger report categories |
| Consumes    | categories.list, transactions.list |

## Purpose

`ledger report categories` reports, for every category, its description, transaction count,
inflow, outflow, and net, followed by a TOTAL row.

## Trigger

The user runs `ledger report categories`.

## Behavior

1. Within the command transaction, read every category through `categories.list`, ordered by
   `category` ascending.
2. For each category, compute by query over `transactions.list`:
   - `transactions`: the number of rows in that category.
   - `inflow`: the sum of positive amounts, in integer cents.
   - `outflow`: the sum of the absolute values of negative amounts, in integer cents, printed as a
     positive number.
   - `net`: `inflow - outflow`.
   A category with no transactions reports `0`, `0.00`, `0.00`, `0.00`.
3. Print the header and one row per category:

```text
category,description,transactions,inflow,outflow,net
```

4. Print the TOTAL row, whose count, inflow, outflow, and net are summed over every transaction:

```text
TOTAL,,<count>,<inflow>,<outflow>,<net>
```

Amounts are formatted per FEATURE-Amount-Format.md. No value is embedded as a constant.

## Routes and Interfaces

| Interface | Kind | Notes |
|---|---|---|
| `ledger report categories` | CLI command | Exit 0 on success. |

## Reads and Writes

| Operation | Access | Repository operation | Notes |
|---|---|---|---|
| List categories | read | `categories.list` | Ordered by code; includes empty categories. |
| List transactions | read | `transactions.list` | Aggregated per category and in total. |

## Programmatic Acceptance

=== AC report-categories-header ===
Intent: The categories report begins with the category header line.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.categories.create(category="RCA1", description="Report Category A")
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    assert out.splitlines()[0] == "category,description,transactions,inflow,outflow,net"
=== END AC report-categories-header ===

=== AC report-categories-includes-empty ===
Intent: A category with no transactions still appears, with zero values.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.categories.create(category="RCB1", description="Report Empty Category")
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    rows = out.splitlines()
    assert rows[1] == "RCB1,Report Empty Category,0,0.00,0.00,0.00"
=== END AC report-categories-includes-empty ===

=== AC report-categories-inflow-outflow ===
Intent: A category's inflow sums its positive amounts and its outflow sums the absolute values of its negative amounts.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RCC1", name="Report Cat Account")
    db.categories.create(category="RCC2", description="Report Cat Two")
    db.transactions.create(txn_id=7201, date="2026-05-01", account="RCC1",
                           category="RCC2", amount=800, memo="in")
    db.transactions.create(txn_id=7202, date="2026-05-01", account="RCC1",
                           category="RCC2", amount=-125, memo="out")
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    rows = out.splitlines()
    assert rows[1] == "RCC2,Report Cat Two,2,8.00,1.25,6.75"
=== END AC report-categories-inflow-outflow ===

=== AC report-categories-ordered-by-code ===
Intent: Category rows are ordered by category code ascending.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.categories.create(category="RCZ1", description="Zulu")
    db.categories.create(category="RCY1", description="Yankee")
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    rows = out.splitlines()
    assert rows[1].startswith("RCY1,")
    assert rows[2].startswith("RCZ1,")
=== END AC report-categories-ordered-by-code ===

=== AC report-categories-total-row ===
Intent: The TOTAL row sums transaction count, inflow, outflow, and net over every category.
Requires: executable=python3; scope=test

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="RCT1", name="Report Cat Total Account")
    db.categories.create(category="RCT2", description="Report Cat Total Two")
    db.transactions.create(txn_id=7301, date="2026-05-01", account="RCT1",
                           category="RCT2", amount=500, memo="in")
    db.transactions.create(txn_id=7302, date="2026-05-01", account="RCT1",
                           category="RCT2", amount=-200, memo="out")
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    assert out.splitlines()[-1] == "TOTAL,,2,5.00,2.00,3.00"
=== END AC report-categories-total-row ===

## User Acceptance

- None.

## Guardrails

- Every category appears, including those with no transactions.
- No count, sum, or total is hardcoded; every value comes from a query.
- Amounts are formatted with two decimals, never floating point; a zero total prints `0.00`,
  never `-0.00`.
