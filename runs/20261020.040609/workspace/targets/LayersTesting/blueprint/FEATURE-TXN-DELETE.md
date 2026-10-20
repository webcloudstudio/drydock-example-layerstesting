# FEATURE: Transaction Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Delete one transaction through `ledger txn delete <id>`. |
| Depends On  | DATABASE.md, FEATURE-TXN-GET.md, FEATURE-TXN-POST.md, FEATURE-NONNEGATIVE-BALANCE.md |
| Provides    | ledger txn delete |
| Consumes    | transactions.get, transactions.list, transactions.delete |

## Purpose

`ledger txn delete <id>` removes one transaction. A deleted id becomes available again: the next
post takes the largest remaining id plus one.

## Behavior

- Read the transaction. An absent id exits 4 and writes nothing.
- Delete the row inside the command's transaction.
- Check that no account balance is below zero after the deletion. A violation exits 3 and rolls back.
- On success, commit and write the header `deleted` and the id.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-delete-removes-row ===
Intent: Deleting a transaction exits 0, writes deleted then the id, and removes the row.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
seeded_cents = 4550
txn_id_value = 1
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=txn_id_value, date=date_value, account=account_code, category=category_code,
        amount=seeded_cents, memo="seed",
    )
txn_id_text = "1"

exit_code, out, err = cli_runner("txn", "delete", txn_id_text)
print(out)
print(err)
assert exit_code == 0
assert out.splitlines() == ["deleted", txn_id_text]
with db_session(dsn) as db:
    assert txn_id_value not in [row.txn_id for row in db.transactions.list()]
=== END AC txn-delete-removes-row ===

=== AC txn-delete-rejects-negative-balance ===
Intent: Deleting a credit that would leave an account balance below zero exits 3 and keeps the row.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
credit_cents = 4550
debit_cents = -1000
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=1, date=date_value, account=account_code, category=category_code,
        amount=credit_cents, memo="sale",
    )
    db.transactions.create(
        txn_id=2, date=date_value, account=account_code, category=category_code,
        amount=debit_cents, memo="payment",
    )
txn_id_text = "1"

exit_code, out, err = cli_runner("txn", "delete", txn_id_text)
print(out)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert 1 in [row.txn_id for row in db.transactions.list()]
=== END AC txn-delete-rejects-negative-balance ===

=== AC txn-delete-absent-id ===
Intent: Deleting a transaction id that does not exist exits 4 and writes nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
absent_id_text = "999"
with db_session(dsn) as db:
    count_before = len(db.transactions.list())

exit_code, out, err = cli_runner("txn", "delete", absent_id_text)
print(out)
print(err)
assert exit_code == 4
assert out == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-delete-absent-id ===

=== AC txn-delete-id-reused ===
Intent: After the largest transaction id is deleted, the next post takes that id again, because the largest remaining id plus one is used.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=1, date=date_value, account=account_code, category=category_code,
        amount=4550, memo="sale",
    )
    db.transactions.create(
        txn_id=2, date=date_value, account=account_code, category=category_code,
        amount=100, memo="sale",
    )
largest_remaining_id = 1
delete_exit, delete_out, delete_err = cli_runner("txn", "delete", "2")
print(delete_err)
assert delete_exit == 0

post_exit, post_out, post_err = cli_runner(
    "txn", "post", account_code, category_code, "1.00", date_value
)
print(post_err)
assert post_exit == 0
assert int(post_out.splitlines()[1].split(",")[0]) == largest_remaining_id + 1
=== END AC txn-delete-id-reused ===

## User Acceptance

- None.

## Guardrails

- `txn delete` never deletes a row for an absent id.
- A deletion that leaves any account balance below zero is never committed.
