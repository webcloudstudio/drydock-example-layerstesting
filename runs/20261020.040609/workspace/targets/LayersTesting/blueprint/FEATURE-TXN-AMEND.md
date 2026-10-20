# FEATURE: Transaction Amend

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Change the amount of one transaction through `ledger txn amend <id> <amount>`. |
| Depends On  | DATABASE.md, FEATURE-TXN-GET.md, FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-AMOUNT.md |
| Provides    | ledger txn amend |
| Consumes    | transactions.get, transactions.list, transactions.update |

## Purpose

`ledger txn amend <id> <amount>` replaces the amount of one transaction. No other field changes.

## Behavior

- Validate the amount with the amount rule. A violation exits 3.
- Read the transaction. An absent id exits 4 and writes nothing.
- Update only the `amount` field inside the command's transaction.
- Check that no account balance is below zero after the change. A violation exits 3 and rolls back.
- On success, commit and write the header `txn_id,date,account,category,amount,memo` and the updated
  row.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-amend-changes-only-amount ===
Intent: Amending a transaction exits 0, stores the new amount, and leaves date, account, category, and memo unchanged.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
memo_value = "walk in sale"
seeded_cents = 4550
txn_id_value = 1
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=txn_id_value, date=date_value, account=account_code, category=category_code,
        amount=seeded_cents, memo=memo_value,
    )
txn_id_text = "1"
new_amount_text = "54.50"
new_cents = 5450

exit_code, out, err = cli_runner("txn", "amend", txn_id_text, new_amount_text)
print(out)
print(err)
assert exit_code == 0
assert out.splitlines()[0] == "txn_id,date,account,category,amount,memo"
with db_session(dsn) as db:
    row = db.transactions.get(txn_id=txn_id_value)
    assert row.amount == new_cents
    assert row.date == date_value
    assert row.account == account_code
    assert row.category == category_code
    assert row.memo == memo_value
=== END AC txn-amend-changes-only-amount ===

=== AC txn-amend-rejects-negative-balance ===
Intent: An amendment that would leave an account balance below zero exits 3 and leaves the stored amount unchanged.

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
overdraw_amount = "-1.00"

exit_code, out, err = cli_runner("txn", "amend", txn_id_text, overdraw_amount)
print(out)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert db.transactions.get(txn_id=txn_id_value).amount == seeded_cents
=== END AC txn-amend-rejects-negative-balance ===

=== AC txn-amend-absent-id ===
Intent: Amending a transaction id that does not exist exits 4 and writes nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
absent_id_text = "999"
with db_session(dsn) as db:
    count_before = len(db.transactions.list())

exit_code, out, err = cli_runner("txn", "amend", absent_id_text, "1.00")
print(out)
print(err)
assert exit_code == 4
assert out == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-amend-absent-id ===

=== AC txn-amend-rejects-invalid-amount ===
Intent: An amount of zero exits 3 and leaves the stored amount unchanged.

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
zero_amount = "0"

exit_code, out, err = cli_runner("txn", "amend", txn_id_text, zero_amount)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert db.transactions.get(txn_id=txn_id_value).amount == seeded_cents
=== END AC txn-amend-rejects-invalid-amount ===

## User Acceptance

- None.

## Guardrails

- `txn amend` never changes `txn_id`, `date`, `account`, `category`, or `memo`.
- An amendment that leaves any account balance below zero is never committed.
