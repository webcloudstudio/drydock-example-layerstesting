# FEATURE: Transaction Amend

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn amend <id> <amount>` changing only the amount under the non-negative balance rule. |
| Depends On | FEATURE-TxnGet.md, DATABASE.md |
| Provides | ledger txn amend |
| Consumes | ledger txn get |

## Purpose

Correct the amount of a stored transaction through the `txn` verb table in `cli/commands/txn.py`.

## Behavior

1. Usage: `ledger txn amend <id> <amount>`; any other argument count is a usage error (exit 2).
2. The id must be decimal digits and the amount valid (at most two decimals, never zero), else exit 3.
3. An absent id exits 4.
4. The account's balance after the change must not be negative, else exit 3 and nothing changes.
5. Only the amount changes. Output is the header and the updated row read back from storage.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-amend-success ===
Intent: Amend changes only the amount, prints the updated row, and a separate read shows other fields untouched.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTAMD1"
cat = "ZZTACAT1"
date = "2026-04-01"
memo = "walk in sale"
new_amount_arg = "54.50"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend One")
    db.categories.create(category=cat, description="Amend Cat")
    txn_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=4550, memo=memo
    )
    exit_code, out, err = cli_runner("txn", "amend", str(txn_id), new_amount_arg)
    print(out)
    print(err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), date, acct, cat, new_amount_arg, memo]
    back = db.transactions.get(txn_id=txn_id)
    assert back is not None
    assert back.amount == 5450
    assert back.date == date
    assert back.account == acct
    assert back.category == cat
    assert back.memo == memo
=== END AC txn-amend-success ===

=== AC txn-amend-rejects-negative-balance ===
Intent: Reducing an inflow so the account balance would go negative exits 3 and leaves the stored amount unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTAMD2"
cat = "ZZTACAT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Two")
    db.categories.create(category=cat, description="Amend Cat Two")
    inflow_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    outflow_id = inflow_id + 1
    db.transactions.create(
        txn_id=inflow_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo="in"
    )
    db.transactions.create(
        txn_id=outflow_id, date="2026-04-02", account=acct, category=cat, amount=-500, memo="out"
    )
    exit_code, out, err = cli_runner("txn", "amend", str(inflow_id), "1.00")
    print(out, err)
    assert exit_code == 3
    assert out == ""
    unchanged = db.transactions.get(txn_id=inflow_id)
    assert unchanged is not None
    assert unchanged.amount == 1000
=== END AC txn-amend-rejects-negative-balance ===

=== AC txn-amend-rejects-invalid-amount ===
Intent: A three-decimal amount, a zero amount and a non-digit id each exit 3 and change nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTAMD3"
cat = "ZZTACAT3"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Three")
    db.categories.create(category=cat, description="Amend Cat Three")
    txn_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=800, memo="m"
    )
    for args in ((str(txn_id), "1.234"), (str(txn_id), "0.00"), ("abc", "1.00")):
        exit_code, out, err = cli_runner("txn", "amend", *args)
        print(args, exit_code, out, err)
        assert exit_code == 3
        assert out == ""
    still = db.transactions.get(txn_id=txn_id)
    assert still is not None
    assert still.amount == 800
=== END AC txn-amend-rejects-invalid-amount ===

=== AC txn-amend-absent ===
Intent: Amending an id no transaction holds exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    missing = max([r.txn_id for r in db.transactions.list()], default=0) + 1000
    exit_code, out, err = cli_runner("txn", "amend", str(missing), "1.00")
    print(out)
    print(err)
    assert exit_code == 4
    assert out == ""
    assert db.transactions.get(txn_id=missing) is None
=== END AC txn-amend-absent ===

=== AC txn-amend-usage ===
Intent: Amend with a missing amount argument is a usage error with exit 2.

from cli.testing import cli_runner

exit_code, out, err = cli_runner("txn", "amend", "1")
print(out)
print(err)
assert exit_code == 2
assert out == ""
=== END AC txn-amend-usage ===

## User Acceptance

- None.

## Guardrails

- Only the amount of a transaction can change.
- The balance check completes before the write; a rejected amend changes nothing.
- Amounts are integer cents; no floating point.
- Diagnostics go to standard error only.
