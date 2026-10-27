# FEATURE: Transaction Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn delete <id>`, which removes one transaction unless the removal would leave an account balance below zero. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger txn delete |
| Consumes | ledger, transactions |

## Purpose

Remove a single stored transaction by id. The command validates everything before it writes, and a rejected command changes nothing.

## Interface

`ledger txn delete <id>`

| Outcome | Exit | Standard output |
|---------|------|-----------------|
| Deleted | 0 | CSV rows `deleted` and the id |
| Id not stored | 4 | nothing |
| Id not an integer | 3 | nothing |
| Removal would leave the owning account balance below zero | 3 | nothing |

## Behavior

1. Parse the id as an integer. A value that is not an integer is rejected with exit 3 before any lookup.
2. Look the transaction up through `db.transactions.get`. An absent id exits 4 (not-found is checked before the balance rule).
3. Compute the owning account's balance after removal, in integer cents, from `db.transactions.list(account=...)`. If it is below zero, exit 3 and write nothing.
4. Remove the row with `db.transactions.delete`, then write `deleted` and the id as CSV (`\n` line endings, no quoting).
5. Diagnostics go to standard error only.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-delete-removes-row ===
Intent: Deleting a stored transaction exits 0, prints the deleted marker and the id, and a separate read finds the row gone while its sibling remains.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX1"
cat = "ZQX1"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Acct")
    db.categories.create(category=cat, description="Delete Cat")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=acct, category=cat, amount=100000, memo="")
    db.transactions.create(txn_id=base + 1, date="2026-06-02", account=acct, category=cat, amount=-30000, memo="")
    code, out, err = cli_runner("txn", "delete", str(base + 1))
    print(out)
    print(err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["deleted"], [str(base + 1)]]
    assert db.transactions.get(txn_id=base + 1) is None
    assert db.transactions.get(txn_id=base) is not None
=== END AC txn-delete-removes-row ===

=== AC txn-delete-absent-id ===
Intent: Deleting an id that is not stored exits 4, writes nothing to standard output, and leaves the stored row count unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = db.transactions.list()
    absent = max([r.txn_id for r in before] or [0]) + 1000
    code, out, err = cli_runner("txn", "delete", str(absent))
    print(out)
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.transactions.list()) == len(before)
=== END AC txn-delete-absent-id ===

=== AC txn-delete-negative-balance ===
Intent: Deleting a deposit that backs a later withdrawal would leave the balance below zero, so the command exits 3, prints nothing, and keeps both rows.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX2"
cat = "ZQX2"
with db_session() as db:
    db.accounts.create(account=acct, name="Guard Acct")
    db.categories.create(category=cat, description="Guard Cat")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=acct, category=cat, amount=100000, memo="")
    db.transactions.create(txn_id=base + 1, date="2026-06-02", account=acct, category=cat, amount=-30000, memo="")
    code, out, err = cli_runner("txn", "delete", str(base))
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=base) is not None
    assert db.transactions.get(txn_id=base + 1) is not None
    assert sum(t.amount for t in db.transactions.list(account=acct)) == 70000
=== END AC txn-delete-negative-balance ===

=== AC txn-delete-non-integer-id ===
Intent: A non-integer id is a rejected input, so the command exits 3, prints nothing, and removes no transaction.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", "abc")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-delete-non-integer-id ===

## User Acceptance

- None.

## Guardrails

- A rejected delete changes no stored record.
- The balance rule is evaluated before the first write.
- Amounts are integer cents; no floating point.
- Only the persistence package is used to reach the store; no database driver is imported.
