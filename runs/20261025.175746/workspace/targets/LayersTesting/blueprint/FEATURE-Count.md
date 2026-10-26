# FEATURE: Count

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The ledger count command reports the number of rows in each table. |
| Depends On | FEATURE-CliFoundation.md, DATABASE.md |
| Provides | ledger count |
| Consumes | accounts.list, categories.list, transactions.list |

## Purpose

`ledger count` prints a CSV of row counts per table, read from the database at run time.

## Behavior

- Takes no arguments; any argument is a usage error (exit 2).
- Prints the header `table,rows`, then the rows `accounts`, `categories`, `transactions` in that
  order, each with its stored row count, and exits 0.

## Database Interface

- `FEATURE-ACCOUNTS-003` — read: count accounts from the listed rows - supplies: `account` - returns: `account`
- `FEATURE-CATEGORIES-003` — read: count categories from the listed rows - supplies: `category` - returns: `category`
- `FEATURE-TRANSACTIONS-003` — read: count transactions from the listed rows - supplies: `account` - returns: `txn_id`

## Programmatic Acceptance

=== AC count-reports-stored-rows ===
Intent: Count prints the table header and the stored row count of each table in the declared order.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "UTCNT1"
cat = "UTCNTC1"
with db_session() as db:
    db.accounts.create(account=acct, name="Count Probe")
    db.categories.create(category=cat, description="Count Category")
    db.transactions.create(
        txn_id=960001, date="2026-04-01", account=acct, category=cat, amount=100, memo=""
    )
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
    assert int(rows[1][1]) == len(db.accounts.list())
    assert int(rows[2][1]) == len(db.categories.list())
    assert int(rows[3][1]) == len(db.transactions.list())
=== END AC count-reports-stored-rows ===

=== AC count-tracks-changes ===
Intent: Count reflects rows added after a previous count.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner


def accounts_count():
    code, out, err = cli_runner("count")
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return int(rows[1][1])


with db_session() as db:
    before = accounts_count()
    db.accounts.create(account="UTCNT2A", name="One")
    db.accounts.create(account="UTCNT2B", name="Two")
    assert accounts_count() == before + 2
=== END AC count-tracks-changes ===

=== AC count-after-init ===
Intent: After init every table reports zero rows.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="UTCNT3", name="Gone")
    assert cli_runner("init")[0] == 0
    code, out, err = cli_runner("count")
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert [int(r[1]) for r in rows[1:]] == [0, 0, 0]
=== END AC count-after-init ===

=== AC count-argument-usage ===
Intent: Count with an extra argument is a usage error with no standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
print(err)
assert code == 2
assert out == ""
=== END AC count-argument-usage ===

## User Acceptance

- None.

## Guardrails

- Counts come from queries, never from stored or embedded values.
- Count writes nothing to the database.
