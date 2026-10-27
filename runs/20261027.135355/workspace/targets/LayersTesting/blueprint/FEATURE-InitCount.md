# FEATURE: Init and Count

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The `ledger init` command that empties the ledger and the `ledger count` command that reports table row counts. |
| Depends On | FEATURE-CliEntry.md, DATABASE.md, ARCHITECTURE.md |
| Provides | ledger init, ledger count |
| Consumes | ledger, cli.registry |

## Purpose

`init` prepares an empty ledger for loading and use. `count` reports how many rows each table holds. Both are registered in `cli/commands/maintenance.py` through its `COMMANDS` mapping, with keys `("init",)` and `("count",)`, each taking no arguments.

## Behavior

### `ledger init`

- Opens the database through the entry point; opening creates the database file and declared schema when they do not yet exist.
- Removes every row from `transactions`, then `categories`, then `accounts` (foreign-key order).
- Returns no rows, so nothing is written to stdout, and exits `0`.
- Running it again on an empty ledger also exits `0`.

### `ledger count`

- Output is CSV: header `table,rows`, then the rows `accounts`, `categories`, `transactions` in that order, each with the number of rows stored, read from the database.
- Counts are never embedded; they are computed from the repository `list` results.

An argument given to either command is a usage error (exit 2).

## Database Interface

- `FEATURE-ACCOUNT-005` — read: list accounts to count them - supplies: — - returns: `account`
- `FEATURE-CATEGORY-005` — read: list categories to count them - supplies: — - returns: `category`
- `FEATURE-TXN-005` — read: list transactions to count them - supplies: — - returns: `txn_id`
- `FEATURE-TXN-006` — write: remove every transaction on init - supplies: `min_txn_id` - returns: —
- `FEATURE-CATEGORY-006` — write: remove every category on init - supplies: `min_category` - returns: —
- `FEATURE-ACCOUNT-006` — write: remove every account on init - supplies: `min_account` - returns: —

## Programmatic Acceptance

=== AC count-shape ===
Intent: count prints the header table,rows and the three tables in order, each count equal to the number of stored rows.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

code, out, err = cli_runner("count")
print(code, repr(out), repr(err))
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["table", "rows"]
assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
with db_session() as db:
    expected = [len(db.accounts.list()), len(db.categories.list()), len(db.transactions.list())]
assert [int(r[1]) for r in rows[1:]] == expected
=== END AC count-shape ===

=== AC count-tracks-writes ===
Intent: After one account, one category, and one transaction are stored, each reported count rises by exactly one.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def counts():
    code, out, err = cli_runner("count")
    assert code == 0, err
    return [int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]]

before = counts()
with db_session() as db:
    db.accounts.create(account="ZZCNT1", name="Count Probe")
    db.categories.create(category="ZZCNTC", description="Count Cat")
    db.transactions.create(txn_id=900200001, date="2026-05-01", account="ZZCNT1",
                           category="ZZCNTC", amount=100, memo="")
after = counts()
assert after == [n + 1 for n in before]
=== END AC count-tracks-writes ===

=== AC init-empties-tables ===
Intent: init exits 0 with empty stdout, removes rows in foreign-key order without error, and leaves all three tables empty.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="ZZINI1", name="Init Probe")
    db.categories.create(category="ZZINIC", description="Init Cat")
    db.transactions.create(txn_id=900200011, date="2026-05-01", account="ZZINI1",
                           category="ZZINIC", amount=100, memo="")
code, out, err = cli_runner("init")
print(code, repr(out), repr(err))
assert code == 0
assert out == ""
with db_session() as db:
    assert len(db.transactions.list()) == 0
    assert len(db.categories.list()) == 0
    assert len(db.accounts.list()) == 0
=== END AC init-empties-tables ===

=== AC init-then-count ===
Intent: After init, count reports zero rows for every table, and init run a second time on the empty ledger still exits 0.

import csv
import io
from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0, err
code, out, err = cli_runner("init")
assert code == 0, err
assert out == ""
code, out, err = cli_runner("count")
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["table", "rows"]
assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
assert [int(r[1]) for r in rows[1:]] == [0, 0, 0]
=== END AC init-then-count ===

=== AC init-fresh-database ===
Intent: init against a database path that does not yet exist creates the file, exits 0, and count then reports zero rows.

import csv
import io
import os
from drydock_acceptance import database_environment
from cli.testing import cli_runner

with database_environment(url="fresh.db") as root:
    assert not os.path.exists(root / "fresh.db")
    code, out, err = cli_runner("init")
    print(code, repr(out), repr(err))
    assert code == 0
    assert os.path.exists(root / "fresh.db")
    code, out, err = cli_runner("count")
    assert code == 0, err
    rows = list(csv.reader(io.StringIO(out)))
    assert [int(r[1]) for r in rows[1:]] == [0, 0, 0]
=== END AC init-fresh-database ===

=== AC init-count-usage ===
Intent: init and count with an extra argument are usage errors that exit 2 with empty stdout.

from cli.testing import cli_runner

for args in [("init", "extra"), ("count", "extra")]:
    code, out, err = cli_runner(*args)
    print(args, code, repr(out), repr(err))
    assert code == 2
    assert out == ""
=== END AC init-count-usage ===

## User Acceptance

- None.

## Guardrails

- `init` writes nothing to standard output.
- Counts are read from the database on every run and are never embedded.
- `init` removes rows in foreign-key order: transactions, then categories, then accounts.
- Amounts and counts use no floating point.
