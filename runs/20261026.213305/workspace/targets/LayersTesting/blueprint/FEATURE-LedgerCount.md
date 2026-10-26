# FEATURE: Ledger Count

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implement `ledger count` reporting stored row counts for the three tables. |
| Depends On | FEATURE-LedgerInit.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger count |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows |

## Purpose

`ledger count` reports how many rows each table holds, computed from the database each time.

## Rules

- Register `count` through `ledger.register_command`; it takes no arguments.
- Output is the header `table,rows` followed by `accounts`, `categories`, `transactions` rows in that order, each with its stored row count, written through `csv_output.write_rows`.
- Each count is the length of the matching repository `list`; nothing is cached or embedded.
- Exit 0 on success. Database failures follow the error contract (exit 1).

## Database Interface

- `FEATURE-ACCOUNT-003` — read: list all accounts - supplies: none - returns: `account`, `name`
- `FEATURE-CATEGORY-003` — read: list all categories - supplies: none - returns: `category`, `description`
- `FEATURE-TXN-003` — read: list all transactions - supplies: none - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC count-matches-stored-rows ===
Intent: count reports the header and the three table row counts in fixed order, matching the store.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="ZQCNT1", name="Count One")
    db.accounts.create(account="ZQCNT2", name="Count Two")
    db.categories.create(category="ZQCNTC1", description="Count Cat")
    db.transactions.create(
        txn_id=930001, date="2026-04-01", account="ZQCNT1", category="ZQCNTC1", amount=250, memo=""
    )
    code, out, err = cli_runner("count")
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    expected = [
        ["table", "rows"],
        ["accounts", str(len(db.accounts.list()))],
        ["categories", str(len(db.categories.list()))],
        ["transactions", str(len(db.transactions.list()))],
    ]
    assert rows == expected
=== END AC count-matches-stored-rows ===

=== AC count-after-init ===
Intent: After init every count is zero.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="ZQCNT3", name="Count Three")
    code, out, err = cli_runner("init")
    assert code == 0
    code, out, err = cli_runner("count")
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
    assert [r[1] for r in rows[1:]] == ["0", "0", "0"]
=== END AC count-after-init ===

=== AC count-uses-lf-line-endings ===
Intent: count output has four newline-terminated lines with no carriage returns.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session():
    code, out, err = cli_runner("count")
    assert code == 0
    assert "\r" not in out
    assert out.endswith("\n")
    assert len(out.splitlines()) == 4
=== END AC count-uses-lf-line-endings ===

=== AC count-wrong-argument-count ===
Intent: count with an extra argument is a usage error with empty stdout.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
assert code == 2
assert out == ""
=== END AC count-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- Counts come from database queries, never from embedded values.
- A failing command writes nothing to standard output.
