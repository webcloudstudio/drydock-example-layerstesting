# FEATURE: Txn Delete

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger txn delete <id>`, which removes a transaction only when no balance would go negative. |
| Depends On | FEATURE-TxnPost.md, FEATURE-BalanceRules.md, FEATURE-CsvOutput.md, FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger txn delete |
| Consumes | ledger.register_command, persistence.open_database, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected |

## Purpose

Remove one transaction by id. Deleting a receipt can push an account negative, so the balance rule is applied to the state after the deletion.

## Behavior

- Invocation: `ledger txn delete <id>` with exactly one argument.
- A non-integer id exits 3. An integer id with no stored row exits 4.
- The account's balance without this row is checked with `balance_rules.check_final_balances`; a negative result exits 3 and changes nothing.
- Success deletes the row and writes two lines: `deleted`, then the id.
- Read, check and delete run in one database transaction.

## Database Interface

- `FEATURE-TXN-002` — read: get the transaction - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-003` — read: list the account's transactions for the balance check - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-005` — write: delete the transaction - supplies: `txn_id` - returns: `txn_id`

## Programmatic Acceptance

=== AC txn-delete-success ===
Intent: Deleting a transaction prints deleted and the id and removes the row.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQDL1"
cat = "ZQDLC1"
txn_id = 940001
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=-1234, memo="" 
    ) if False else None
    db.transactions.create(txn_id=txn_id + 1, date="2026-04-01", account=acct, category=cat, amount=5000, memo="")
    db.transactions.create(txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=-1234, memo="tape")
    code, out, err = cli_runner("txn", "delete", str(txn_id))
    print(out)
    print(err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["deleted"], [str(txn_id)]]
    assert db.transactions.get(txn_id=txn_id) is None
    assert db.transactions.get(txn_id=txn_id + 1) is not None
=== END AC txn-delete-success ===

=== AC txn-delete-negative-rejected ===
Intent: A deletion that would leave the account balance negative exits 3 and keeps every row.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQDL2"
cat = "ZQDLC2"
a_id, b_id = 940021, 940022
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=a_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="")
    db.transactions.create(txn_id=b_id, date="2026-04-02", account=acct, category=cat, amount=-6000, memo="")
    code, out, err = cli_runner("txn", "delete", str(a_id))
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=a_id) is not None
    assert db.transactions.get(txn_id=b_id) is not None
=== END AC txn-delete-negative-rejected ===

=== AC txn-delete-positive-allowed ===
Intent: Deleting a receipt succeeds when the remaining balance is still non-negative.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQDL3"
cat = "ZQDLC3"
a_id, b_id = 940031, 940032
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=a_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="")
    db.transactions.create(txn_id=b_id, date="2026-04-02", account=acct, category=cat, amount=5000, memo="")
    code, out, err = cli_runner("txn", "delete", str(b_id))
    print(out)
    print(err)
    assert code == 0
    assert db.transactions.get(txn_id=b_id) is None
    assert sum(r.amount for r in db.transactions.list(account=acct)) == 10000
=== END AC txn-delete-positive-allowed ===

=== AC txn-delete-absent ===
Intent: Deleting an absent id exits 4 with nothing on stdout; a non-integer id exits 3.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    ids = [r.txn_id for r in db.transactions.list()]
    absent = (max(ids) if ids else 0) + 1000
    before = len(ids)
    code, out, err = cli_runner("txn", "delete", str(absent))
    print(err)
    assert code == 4
    assert out == ""
    code, out, err = cli_runner("txn", "delete", "abc")
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-delete-absent ===

=== AC txn-delete-then-get ===
Intent: After a successful delete, a second delete of the same id reports not found.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQDL4"
cat = "ZQDLC4"
txn_id = 940041
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=700, memo="")
    code, out, err = cli_runner("txn", "delete", str(txn_id))
    assert code == 0
    code, out, err = cli_runner("txn", "delete", str(txn_id))
    assert code == 4
    assert out == ""
=== END AC txn-delete-then-get ===

## User Acceptance

- None.

## Guardrails

- A rejected deletion removes nothing; the balance check precedes the delete.
- No floating point is used for money at any layer.
- A failing command writes nothing to stdout and never echoes a DSN or credential.
