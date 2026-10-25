# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account delete <code>`, removing an account that has no transactions. |
| Depends On | FEATURE-AccountGet.md, FEATURE-LoadTransactions.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger account delete |
| Consumes | accounts.delete, accounts.list, transactions.list |

## Purpose

Delete an account. An account that still has transactions is refused so that no transaction is orphaned.

## Command Contract

| Aspect | Rule |
|--------|------|
| Invocation | `ledger account delete <code>` with exactly one argument. |
| Success stdout | Two lines: `deleted`, then the code. |
| Absent account | Exit 4, nothing on stdout. |
| Account in use | Exit 3 when the account has any transaction; nothing is deleted and nothing is written to stdout. |
| Check order | Existence and in-use checks complete before the delete. |
| Wrong argument count | Exit 2, nothing on stdout. |

## Database Interface

- `FEATURE-ACCOUNT-005` — write: delete an account - supplies: `account` - returns: `account`
- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: find transactions that reference the account - supplies: `account` - returns: `txn_id`

## Programmatic Acceptance

=== AC account-delete-success ===
Intent: Deleting an account with no transactions prints deleted and the code, and the account no longer reads back.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ADELS1"
    db.accounts.create(account=code, name="Delete Me")
    rc, out, err = cli_runner("account", "delete", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [code]]
    assert db.accounts.get(account=code) is None
=== END AC account-delete-success ===

=== AC account-delete-in-use ===
Intent: Deleting an account that has transactions is refused with exit 3 and changes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ADELU1"
    cat = "ADELUC1"
    db.accounts.create(account=code, name="In Use")
    db.categories.create(category=cat, description="In Use Cat")
    txn_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-05-01", account=code,
        category=cat, amount=500, memo="",
    )
    accounts_before = len(db.accounts.list())
    txns_before = len(db.transactions.list())
    rc, out, err = cli_runner("account", "delete", code)
    print(err)
    assert rc == 3
    assert out == ""
    assert db.accounts.get(account=code) is not None
    assert len(db.accounts.list()) == accounts_before
    assert len(db.transactions.list()) == txns_before
    assert db.transactions.get(txn_id=txn_id) is not None
=== END AC account-delete-in-use ===

=== AC account-delete-absent ===
Intent: Deleting an absent account exits 4 and writes nothing to stdout.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent = "ADELN1"
    assert db.accounts.get(account=absent) is None
    before = len(db.accounts.list())
    rc, out, err = cli_runner("account", "delete", absent)
    print(err)
    assert rc == 4
    assert out == ""
    assert len(db.accounts.list()) == before
=== END AC account-delete-absent ===

=== AC account-delete-leaves-others ===
Intent: Deleting one account leaves every other account in place.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    gone = "ADELO1"
    kept = "ADELO2"
    db.accounts.create(account=gone, name="Gone")
    db.accounts.create(account=kept, name="Kept")
    before = len(db.accounts.list())
    rc, out, err = cli_runner("account", "delete", gone)
    print(err)
    assert rc == 0
    assert len(db.accounts.list()) == before - 1
    got = db.accounts.get(account=kept)
    assert got is not None
    assert got.name == "Kept"
=== END AC account-delete-leaves-others ===

=== AC account-delete-usage ===
Intent: Deleting with a wrong argument count exits 2 and writes nothing to stdout.

from cli.testing import cli_runner

for args in (("account", "delete"), ("account", "delete", "A", "B")):
    rc, out, err = cli_runner(*args)
    assert rc == 2
    assert out == ""
=== END AC account-delete-usage ===

## User Acceptance

- None.

## Guardrails

- An account with transactions is never deleted.
- The in-use and existence checks run before the delete.
- Nothing is written to stdout on failure.
