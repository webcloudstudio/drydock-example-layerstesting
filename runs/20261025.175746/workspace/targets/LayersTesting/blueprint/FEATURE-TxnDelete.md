# FEATURE: Txn Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `ledger txn delete` command removes one stored transaction unless doing so would leave a negative balance. |
| Depends On  | FEATURE-BalanceRules.md, FEATURE-CliFoundation.md, DATABASE.md |
| Provides    | ledger txn delete |
| Consumes    | transactions.get, transactions.delete, transactions.list, check_balances |

## Purpose

`ledger txn delete <id>` removes a recorded transaction. Removing a deposit can drive a balance below zero, so the balance rule is checked first.

## Trigger

An operator runs `./ledger txn delete <id>`.

## Sequence

1. Reject a wrong argument count with exit 2.
2. Reject a non-integer id with exit 3.
3. Read the row with `transactions.get`. An absent id exits 4.
4. List the account's transactions and run `check_balances` with the row removed. A balance below zero exits 3 and the row is kept.
5. Remove the row with `transactions.delete`, print `deleted` and the id on separate lines, and exit 0.

## Output

```text
deleted
<id>
```

## Reads

- `transactions.get`, `transactions.list`

## Writes

- `transactions.delete`, after every check has passed

## Database Interface

- `FEATURE-TRANSACTIONS-002` — read: retrieve the transaction to delete - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-003` — read: list the account's transactions for the balance check - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-005` — write: remove the transaction - supplies: `txn_id` - returns: `txn_id`

## Programmatic Acceptance

=== AC txn-delete-roundtrip ===
Intent: Deleting a stored transaction prints deleted and the id, and a later read finds nothing.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TDEL1"
cat = "TDCAT1"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Delete Category")
    txn_id = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=4550, memo="gone"
    )
    code, out, err = cli_runner("txn", "delete", str(txn_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["deleted"]
    assert rows[1] == [str(txn_id)]
    assert db.transactions.get(txn_id=txn_id) is None
=== END AC txn-delete-roundtrip ===

=== AC txn-delete-absent ===
Intent: Deleting an id that is not stored exits 4 and removes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    absent = max([r.txn_id for r in db.transactions.list()] or [0]) + 1000
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "delete", str(absent))
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-delete-absent ===

=== AC txn-delete-negative-balance ===
Intent: Deleting a deposit that later payments depend on exits 3 and keeps the row.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TDEL2"
cat = "TDCAT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Delete Category")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    deposit = base
    payment = base + 1
    db.transactions.create(
        txn_id=deposit, date="2026-04-01", account=acct, category=cat, amount=1000, memo="in"
    )
    db.transactions.create(
        txn_id=payment, date="2026-04-02", account=acct, category=cat, amount=-500, memo="out"
    )
    code, out, err = cli_runner("txn", "delete", str(deposit))
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=deposit) is not None
    assert db.transactions.get(txn_id=payment) is not None
    code, out, err = cli_runner("txn", "delete", str(payment))
    assert code == 0
    assert db.transactions.get(txn_id=payment) is None
=== END AC txn-delete-negative-balance ===

=== AC txn-delete-bad-arguments ===
Intent: A non-integer id exits 3 and a wrong argument count exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("txn", "delete", "abc")
assert code == 3
assert out == ""
code, out, err = cli_runner("txn", "delete")
assert code == 2
assert out == ""
code, out, err = cli_runner("txn", "delete", "1", "2")
assert code == 2
assert out == ""
=== END AC txn-delete-bad-arguments ===

## User Acceptance

- None.

## Guardrails

- The balance check completes before the delete; a rejected delete keeps every row.
- Only the named transaction is removed; no other row is touched.
- Diagnostics go to standard error only.
