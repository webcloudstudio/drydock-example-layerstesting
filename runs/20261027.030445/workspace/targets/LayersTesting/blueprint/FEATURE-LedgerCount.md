# FEATURE: Ledger Count

| Field       | Value |
|-------------|-------|
| Version     | 20261027 V1 |
| Description | The `ledger count` command reports the number of rows in each table. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-LedgerCli.md |
| Provides    | ledger count |
| Consumes    | ledger |

## Purpose

`ledger count` shows how many accounts, categories, and transactions are stored.

## Behavior

- Takes no arguments; any argument is a usage error (exit 2).
- Writes the header `table,rows`, then the rows `accounts`, `categories`, `transactions` in that order, each with its stored row count. Counts come from the list operations of the database, never from embedded numbers.
- Exits 0. When the database cannot be opened it exits 1 with empty standard output and changes nothing.
- The handler is registered as `("count",)` and returns the CSV rows.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC count-reports-stored-rows ===
Intent: count writes the header and the three tables in the declared order, with counts equal to what the store holds after setup.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="ZQN1", name="Count Account")
    db.categories.create(category="ZQN1", description="Count Category")
    db.transactions.create(
        txn_id=930001, date="2026-06-01", account="ZQN1", category="ZQN1", amount=1000, memo=""
    )
    want = {
        "accounts": len(db.accounts.list()),
        "categories": len(db.categories.list()),
        "transactions": len(db.transactions.list()),
    }
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
    for name, n in rows[1:]:
        assert int(n) == want[name]
    assert want["accounts"] >= 1
    assert want["transactions"] >= 1
=== END AC count-reports-stored-rows ===

=== AC count-after-init-is-zero ===
Intent: After init the three counts are zero, and the output has exactly the header plus three rows.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 4
    assert [row[0] for row in rows] == ["table", "accounts", "categories", "transactions"]
    assert [int(row[1]) for row in rows[1:]] == [0, 0, 0]
=== END AC count-after-init-is-zero ===

=== AC count-follows-new-rows ===
Intent: The account count rises by exactly the number of accounts created, read back through a second count invocation.

import csv
import io

from persistence.testing import db_session
from cli.testing import cli_runner


def accounts_count():
    code, out, err = cli_runner("count")
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return int(dict((r[0], r[1]) for r in rows[1:])["accounts"])


with db_session() as db:
    before = accounts_count()
    codes = ["ZQN2", "ZQN3", "ZQN4"]
    for code_value in codes:
        db.accounts.create(account=code_value, name="More " + code_value)
    after = accounts_count()
    assert after == before + len(codes)
=== END AC count-follows-new-rows ===

=== AC count-rejects-arguments ===
Intent: count with an extra argument is a usage error with empty standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
print(out)
print(err)
assert code == 2
assert out == ""
assert len(err.splitlines()) == 1
=== END AC count-rejects-arguments ===

=== AC count-store-unavailable ===
Intent: When the database cannot be opened, count exits 1 with empty standard output.

import os
import shutil
import tempfile

from cli.testing import cli_runner

base = tempfile.mkdtemp()
bad_path = os.path.join(base, "missing-dir", "ledger.db")
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ["DATABASE_URL"] = bad_path
    os.environ.pop("DATABASE_PATH", None)
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 1
    assert out == ""
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    shutil.rmtree(base, ignore_errors=True)
=== END AC count-store-unavailable ===

## User Acceptance

- None.

## Guardrails

- Every count comes from a query; never hardcode a count.
- `count` writes nothing to the database.
- A failing command writes nothing to standard output.
