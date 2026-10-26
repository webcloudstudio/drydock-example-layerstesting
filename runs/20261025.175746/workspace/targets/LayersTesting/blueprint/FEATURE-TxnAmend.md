# FEATURE: Txn Amend

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `ledger txn amend` command changes only the amount of one stored transaction, refusing any change that leaves a negative balance. |
| Depends On  | FEATURE-BalanceRules.md, FEATURE-CliFoundation.md, DATABASE.md |
| Provides    | ledger txn amend |
| Consumes    | transactions.get, transactions.update, transactions.list, check_balances |

## Purpose

`ledger txn amend <id> <amount>` corrects the amount of a recorded transaction. Date, account, category, and memo never change.

## Trigger

An operator runs `./ledger txn amend <id> <amount>`.

## Sequence

1. Reject a wrong argument count with exit 2.
2. Reject a non-integer id or an invalid amount (zero, more than two decimals, malformed) with exit 3.
3. Read the row with `transactions.get`. An absent id exits 4.
4. List the account's transactions and run `check_balances` with the proposed changed amount. A balance below zero exits 3 before any write.
5. Store the new amount with `transactions.update` and print the header row and updated row. Exit 0.

## Output

```text
txn_id,date,account,category,amount,memo
<id>,<date>,<account>,<category>,<new amount with two decimals>,<memo>
```

## Reads

- `transactions.get`, `transactions.list`

## Writes

- `transactions.update` setting only `amount`, after every check has passed

## Database Interface

- `FEATURE-TRANSACTIONS-002` — read: retrieve the transaction to amend - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-003` — read: list the account's transactions for the balance check - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-004` — write: change the amount - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-amend-roundtrip ===
Intent: Amending a deposit prints the updated row and persists only the new amount in integer cents.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TAMD1"
cat = "TACAT1"
when = "2026-04-01"
memo = "amend probe"
new_text = "60.00"
new_cents = 6000
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Amend Category")
    txn_id = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=txn_id, date=when, account=acct, category=cat, amount=5000, memo=memo
    )
    code, out, err = cli_runner("txn", "amend", str(txn_id), new_text)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), when, acct, cat, new_text, memo]
    stored = db.transactions.get(txn_id=txn_id)
    assert stored.amount == new_cents
    assert stored.date == when
    assert stored.account == acct
    assert stored.category == cat
    assert stored.memo == memo
=== END AC txn-amend-roundtrip ===

=== AC txn-amend-absent ===
Intent: Amending an id that is not stored exits 4 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    absent = max([r.txn_id for r in db.transactions.list()] or [0]) + 1000
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "amend", str(absent), "1.00")
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-amend-absent ===

=== AC txn-amend-negative-balance ===
Intent: An amendment that would leave the account balance below zero exits 3 and leaves the amount unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TAMD2"
cat = "TACAT2"
original = 1000
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Amend Category")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    deposit = base
    payment = base + 1
    db.transactions.create(
        txn_id=deposit, date="2026-04-01", account=acct, category=cat, amount=original, memo="in"
    )
    db.transactions.create(
        txn_id=payment, date="2026-04-02", account=acct, category=cat, amount=-500, memo="out"
    )
    code, out, err = cli_runner("txn", "amend", str(deposit), "0.10")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=deposit).amount == original
    assert db.transactions.get(txn_id=payment).amount == -500
=== END AC txn-amend-negative-balance ===

=== AC txn-amend-invalid-amount ===
Intent: A zero or over-precise amount exits 3 and leaves the stored amount unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TAMD3"
cat = "TACAT3"
original = 2500
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Amend Category")
    txn_id = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=original, memo=""
    )
    for bad in ["0", "1.234", "abc"]:
        code, out, err = cli_runner("txn", "amend", str(txn_id), bad)
        print(bad, code, err)
        assert code == 3
        assert out == ""
    assert db.transactions.get(txn_id=txn_id).amount == original
=== END AC txn-amend-invalid-amount ===

=== AC txn-amend-usage ===
Intent: A wrong argument count exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("txn", "amend", "1")
assert code == 2
assert out == ""
code, out, err = cli_runner("txn", "amend", "1", "2.00", "extra")
assert code == 2
assert out == ""
=== END AC txn-amend-usage ===

## User Acceptance

- None.

## Guardrails

- Only the amount changes; date, account, category, and memo are never written.
- The balance check completes before the first write; a rejected amendment changes nothing.
- Amounts are integer cents; floating point is never used for money.
- Diagnostics go to standard error only.
