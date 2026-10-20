# FEATURE: Schema Count

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Implements `ledger count`, which reports the number of rows in each of the three tables. |
| Depends On  | FEATURE-SCHEMA-INIT.md, FEATURE-CSV-OUTPUT.md, DATABASE.md |
| Provides    | ledger count |
| Consumes    | accounts.list, categories.list, transactions.list |

## Purpose

`ledger count` lets the shop confirm how many rows each table holds. Every count is computed from the database at the moment the command runs.

## Behavior

- `ledger count` writes the header `table,rows`, then one row each for `accounts`, `categories`, and `transactions`, in that order.
- Each count is the number of rows returned by the table's `list` operation.
- The output follows the CSV conventions in FEATURE-CSV-OUTPUT.
- The command exits 0 on success.

## Programmatic Acceptance

=== AC count-reports-each-table ===
Intent: After rows are created through the persistence layer, count reports the header and one row per table with counts read back from the database.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as work:
    dsn = os.path.join(work, "ledger.db")
    os.environ["DATABASE_URL"] = dsn
    code, out, err = cli_runner("init")
    assert code == 0
    db = open_database(dsn)
    db.accounts.create(account="CASH1", name="Till")
    db.accounts.create(account="CASH2", name="Safe")
    db.categories.create(category="SALES", description="Sales receipts")
    code, out, err = cli_runner("count")
    print(out)
    print(err, file=sys.stderr)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    expected = [
        ["table", "rows"],
        ["accounts", str(len(db.accounts.list()))],
        ["categories", str(len(db.categories.list()))],
        ["transactions", str(len(db.transactions.list()))],
    ]
    assert rows == expected
=== END AC count-reports-each-table ===

=== AC count-reports-zero-on-empty-store ===
Intent: On an initialized empty store, count exits 0 and every table reports zero rows.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as work:
    dsn = os.path.join(work, "ledger.db")
    os.environ["DATABASE_URL"] = dsn
    code, out, err = cli_runner("init")
    assert code == 0
    code, out, err = cli_runner("count")
    print(out)
    print(err, file=sys.stderr)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [row[1] for row in rows[1:]] == ["0", "0", "0"]
    db = open_database(dsn)
    assert len(db.accounts.list()) == 0
=== END AC count-reports-zero-on-empty-store ===

## User Acceptance

- None.

## Guardrails

- `ledger count` never writes to any table.
- `ledger count` never reports a count that was not read from the database.
