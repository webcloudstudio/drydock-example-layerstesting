# FEATURE: Report Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Implements `ledger report categories`, the per-category inflow, outflow, and net with a TOTAL row. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md |
| Provides    | ledger report categories |
| Consumes    | categories.list, transactions.list |

## Purpose

Report totals by category, computed from stored rows in integer cents, including categories that
have no transactions.

## Trigger

`./ledger report categories`

## Sequence

1. List categories through `categories.list` (ordered by code) and all transactions through `transactions.list`.
2. For each category compute the transaction count, `inflow` (sum of positive amounts), `outflow`
   (sum of absolute values of negative amounts, printed as a positive number), and `net`
   (`inflow - outflow`).
3. Print the header `category,description,transactions,inflow,outflow,net`, one row per category
   ordered by code (empty categories print `0` and `0.00` values), then
   `TOTAL,,<count>,<inflow>,<outflow>,<net>` over all categories.
4. Amounts print with exactly two decimal places, a leading `-` when negative, and no thousands separator.
5. Any argument beyond `categories` is a usage error (exit 2).

## Reads

- `categories.list`, `transactions.list`.

## Writes

- None.

## Database Interface

- `FEATURE-CATEGORIES-003` — read: list categories in code order - supplies: `category` - returns: `category`, `description`
- `FEATURE-TRANSACTIONS-003` — read: list every transaction - supplies: `account` - returns: `txn_id`, `category`, `amount`

## Programmatic Acceptance

=== AC report-categories-row-values ===
Intent: A category's count, inflow, outflow, and net match the cents of the transactions created for it, and an empty category reports zeros.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

acct = "UTSA1"
used = "UTSC1"
unused = "UTSC2"
amounts = [50000, 1999, -1250, -75]
inflow = sum(a for a in amounts if a > 0)
outflow = sum(-a for a in amounts if a < 0)
with db_session() as db:
    db.accounts.create(account=acct, name="Cats")
    db.categories.create(category=used, description="Used")
    db.categories.create(category=unused, description="Unused")
    for offset, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=930001 + offset, date="2026-05-01", account=acct,
            category=used, amount=cents, memo="",
        )
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    by_code = {r[0]: r for r in rows[1:]}
    row = by_code[used]
    assert row[1] == "Used"
    assert int(row[2]) == len(amounts)
    assert to_cents(row[3]) == inflow
    assert to_cents(row[4]) == outflow
    assert to_cents(row[5]) == inflow - outflow
    empty = by_code[unused]
    assert empty[1] == "Unused"
    assert int(empty[2]) == 0
    assert to_cents(empty[3]) == 0
    assert to_cents(empty[4]) == 0
    assert to_cents(empty[5]) == 0
=== END AC report-categories-row-values ===

=== AC report-categories-order-and-total ===
Intent: Category rows are ordered by code and the TOTAL row equals the sums of the category rows and the stored transaction count.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

acct = "UTSB1"
late = "UTSD9"
early = "UTSD1"
with db_session() as db:
    db.accounts.create(account=acct, name="Cats")
    db.categories.create(category=late, description="Late")
    db.categories.create(category=early, description="Early")
    db.transactions.create(
        txn_id=930101, date="2026-05-01", account=acct, category=late, amount=900, memo=""
    )
    db.transactions.create(
        txn_id=930102, date="2026-05-02", account=acct, category=early, amount=-300, memo=""
    )
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    data = rows[1:-1]
    codes = [r[0] for r in data]
    assert codes == sorted(codes)
    assert codes.index(early) < codes.index(late)
    total = rows[-1]
    assert total[0] == "TOTAL"
    assert total[1] == ""
    assert int(total[2]) == sum(int(r[2]) for r in data)
    assert int(total[2]) == len(db.transactions.list())
    assert to_cents(total[3]) == sum(to_cents(r[3]) for r in data)
    assert to_cents(total[4]) == sum(to_cents(r[4]) for r in data)
    assert to_cents(total[5]) == to_cents(total[3]) - to_cents(total[4])
=== END AC report-categories-order-and-total ===

=== AC report-categories-reflects-changes ===
Intent: The report is recomputed from stored rows, so a later outflow raises the category's outflow and lowers its net by exactly its amount.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

def row_for(out, category):
    rows = list(csv.reader(io.StringIO(out)))
    return {r[0]: r for r in rows[1:]}[category]

acct = "UTSE1"
cat = "UTSEC"
deposit = 7000
spend = 2345
with db_session() as db:
    db.accounts.create(account=acct, name="Moves")
    db.categories.create(category=cat, description="Moves")
    db.transactions.create(
        txn_id=930201, date="2026-05-01", account=acct, category=cat, amount=deposit, memo=""
    )
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    before = row_for(out, cat)
    assert to_cents(before[4]) == 0
    db.transactions.create(
        txn_id=930202, date="2026-05-02", account=acct, category=cat, amount=-spend, memo=""
    )
    code, out, err = cli_runner("report", "categories")
    assert code == 0
    after = row_for(out, cat)
    assert int(after[2]) == int(before[2]) + 1
    assert to_cents(after[3]) == deposit
    assert to_cents(after[4]) == spend
    assert to_cents(after[5]) == deposit - spend
=== END AC report-categories-reflects-changes ===

=== AC report-categories-usage ===
Intent: An extra argument after categories exits 2 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session():
    code, out, err = cli_runner("report", "categories", "extra")
    assert code == 2 and out == ""
=== END AC report-categories-usage ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query of stored rows; no row, count, or total is hardcoded or stored.
- Outflow is printed as a positive number; net is inflow minus outflow.
- Money is integer cents internally; no floating point at any layer.
- The command writes nothing to the database.
- Diagnostics go to standard error only.
