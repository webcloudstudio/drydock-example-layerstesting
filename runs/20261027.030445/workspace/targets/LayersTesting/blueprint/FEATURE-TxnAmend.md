# FEATURE: Transaction Amend

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn amend`, which changes only a transaction's amount while keeping every account balance non-negative. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger txn amend |
| Consumes | ledger, transactions |

## Purpose

Correct the amount of a recorded transaction without altering its date, account, category, or memo.

## Trigger

`ledger txn amend <id> <amount>` invoked from the command line.

## Sequence

1. Require exactly two arguments after `amend`; otherwise raise the shared usage error (exit 2).
2. Parse the id as an integer (non-integer exits 3) and look up the transaction. An absent id exits 4; this check runs before the amount is validated.
3. Validate the amount with the shared parser (`-?DIGITS[.D[D]]`, at most two decimals, never zero) into integer cents. Invalid exits 3.
4. Compute the owning account's balance from its stored transactions, replace the old amount with the new one, and confirm the result is not below zero. Otherwise exit 3.
5. Only after every check passes, update the amount and write the header `txn_id,date,account,category,amount,memo` and the updated row.

## Database Interface

- `FEATURE-TXN-002` — read: get the transaction by id - supplies: `txn_id` - returns: `txn_id`, `account`, `amount`
- `FEATURE-TXN-005` — read: list the account's transactions to compute the resulting balance - supplies: `account` - returns: `txn_id`, `amount`
- `FEATURE-TXN-003` — write: change the amount - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Behavior Rules

- Only the amount changes.
- A rejected amend changes no stored record.
- Money is integer cents at every layer.

## Programmatic Acceptance

=== AC txn-amend-success ===
Intent: Amending an amount exits 0, writes the updated row, changes only the amount in storage, and a separate read shows the new cents.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTA1"
cat = "ZTA1"
txn_id = 950001
date = "2026-04-01"
memo = "walk in sale"
old_cents = 4550
new_text = "54.50"
new_cents = 5450
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=old_cents, memo=memo
    )
    exit_code, out, err = cli_runner("txn", "amend", str(txn_id), new_text)
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), date, acct, cat, new_text, memo]
    back = db.transactions.get(txn_id=txn_id)
    assert back is not None
    assert back.amount == new_cents
    assert back.date == date
    assert back.account == acct
    assert back.category == cat
    assert back.memo == memo
=== END AC txn-amend-success ===

=== AC txn-amend-absent ===
Intent: Amending an id that is not stored exits 4, and the not-found check wins over an invalid amount.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    stored = [r.txn_id for r in db.transactions.list()]
    absent = (max(stored) + 1000) if stored else 999
    for amount in ("5.00", "1.234"):
        exit_code, out, err = cli_runner("txn", "amend", str(absent), amount)
        print(amount, exit_code, out, err)
        assert exit_code == 4
        assert out == ""
    assert db.transactions.get(txn_id=absent) is None
=== END AC txn-amend-absent ===

=== AC txn-amend-negative-balance-rejected ===
Intent: An amendment that would leave the account balance below zero exits 3 and the stored amount is unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTA2"
cat = "ZTA2"
receipt_id = 950011
payment_id = 950012
receipt_cents = 10000
payment_cents = -6000
too_small_text = "50.00"
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Account")
    db.categories.create(category=cat, description="Balance Category")
    db.transactions.create(
        txn_id=receipt_id, date="2026-04-01", account=acct, category=cat,
        amount=receipt_cents, memo="",
    )
    db.transactions.create(
        txn_id=payment_id, date="2026-04-02", account=acct, category=cat,
        amount=payment_cents, memo="",
    )
    exit_code, out, err = cli_runner("txn", "amend", str(receipt_id), too_small_text)
    print(exit_code, out, err)
    assert exit_code == 3
    assert out == ""
    back = db.transactions.get(txn_id=receipt_id)
    assert back is not None
    assert back.amount == receipt_cents
=== END AC txn-amend-negative-balance-rejected ===

=== AC txn-amend-balance-allowed ===
Intent: An amendment that keeps the account balance at or above zero is accepted and stored.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTA3"
cat = "ZTA3"
receipt_id = 950021
payment_id = 950022
receipt_cents = 10000
payment_cents = -6000
new_text = "70.00"
new_cents = 7000
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Account")
    db.categories.create(category=cat, description="Balance Category")
    db.transactions.create(
        txn_id=receipt_id, date="2026-04-01", account=acct, category=cat,
        amount=receipt_cents, memo="",
    )
    db.transactions.create(
        txn_id=payment_id, date="2026-04-02", account=acct, category=cat,
        amount=payment_cents, memo="",
    )
    exit_code, out, err = cli_runner("txn", "amend", str(receipt_id), new_text)
    print(exit_code, out, err)
    assert exit_code == 0
    back = db.transactions.get(txn_id=receipt_id)
    assert back is not None
    assert back.amount == new_cents
=== END AC txn-amend-balance-allowed ===

=== AC txn-amend-invalid-amount ===
Intent: Amounts with too many decimals, zero, or non-numeric text are rejected with exit 3 and the stored amount is unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTA4"
cat = "ZTA4"
txn_id = 950031
cents = 2500
bad_amounts = ["1.234", "0", "0.00", "abc"]
with db_session() as db:
    db.accounts.create(account=acct, name="Invalid Account")
    db.categories.create(category=cat, description="Invalid Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=cents, memo=""
    )
    for bad in bad_amounts:
        exit_code, out, err = cli_runner("txn", "amend", str(txn_id), bad)
        print(bad, exit_code, out, err)
        assert exit_code == 3
        assert out == ""
        back = db.transactions.get(txn_id=txn_id)
        assert back is not None
        assert back.amount == cents
=== END AC txn-amend-invalid-amount ===

=== AC txn-amend-non-integer-id ===
Intent: A non-integer id is rejected with exit 3 and writes nothing to standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    exit_code, out, err = cli_runner("txn", "amend", "abc", "5.00")
    print(exit_code, out, err)
    assert exit_code == 3
    assert out == ""
=== END AC txn-amend-non-integer-id ===

## User Acceptance

- None.

## Guardrails

- Only the amount of a transaction may change.
- Every rule is checked before the update; a rejected amend changes nothing.
- Persistence is reached only through the generated persistence package.
