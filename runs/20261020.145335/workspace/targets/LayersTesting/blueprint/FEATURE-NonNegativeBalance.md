# FEATURE: Non-Negative Balance

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reject any command whose changes would leave an account balance below zero. |
| Depends On  | FEATURE-CommandTransaction.md, DATABASE.md |
| Provides    | balance.ensure_non_negative(db, accounts) |
| Consumes    | db.accounts.list, db.transactions.list |

## Purpose

Guards every mutating command. After a command's writes and before its transaction commits, the
command passes the accounts it touched to `balance.ensure_non_negative`. The function computes each
named account's balance as the sum of its transaction amounts, in integer cents, from the database.
If any balance is below zero it raises `RejectedError` with `exit_code` set to `3`. The caller then
rolls back the command's transaction, so no table changes.

## Interface

- `balance.ensure_non_negative(db, accounts)`: `accounts` is an iterable of account codes. Returns
  `None` when every named balance is zero or positive. Raises `balance.RejectedError` otherwise.
- `balance.RejectedError`: carries `exit_code`, which is `3`.
- Reads: `db.accounts.list` to confirm each named account exists, and `db.transactions.list` to sum
  amounts per account. Writes nothing.

## Behavior

1. Sum the `amount` integer-cent values of every transaction whose `account` equals each named code.
2. An account with no transactions has balance `0`.
3. A balance below `0` raises `RejectedError` for the first offending account in code order.
4. Amounts are never converted to floating point at any step.

## Programmatic Acceptance

=== AC nonneg-rejects-negative-balance ===
Intent: A balance below zero raises RejectedError with exit code 3.
import tempfile
import os

from persistence import open_database
from balance import RejectedError, ensure_non_negative

work = tempfile.mkdtemp()
db = open_database(os.path.join(work, "ledger.db"))
db.categories.create(category="OPENING", description="Opening balance")
db.accounts.create(account="CASH1", name="Till")
db.transactions.create(txn_id=1, date="2026-01-01", account="CASH1", category="OPENING", amount=-500, memo="")

expected_exit = 3
raised = None
try:
    ensure_non_negative(db, ["CASH1"])
except RejectedError as error:
    raised = error
print("raised:", raised)
assert raised is not None
assert raised.exit_code == expected_exit
=== END AC nonneg-rejects-negative-balance ===

=== AC nonneg-accepts-zero-balance ===
Intent: A balance of exactly zero does not raise.
import tempfile
import os

from persistence import open_database
from balance import ensure_non_negative

work = tempfile.mkdtemp()
db = open_database(os.path.join(work, "ledger.db"))
db.categories.create(category="OPENING", description="Opening balance")
db.accounts.create(account="CASH1", name="Till")
db.transactions.create(txn_id=1, date="2026-01-01", account="CASH1", category="OPENING", amount=500, memo="")
db.transactions.create(txn_id=2, date="2026-01-02", account="CASH1", category="OPENING", amount=-500, memo="")

ensure_non_negative(db, ["CASH1"])
=== END AC nonneg-accepts-zero-balance ===

=== AC nonneg-sums-all-transactions ===
Intent: The balance is the sum of all transactions, so a positive total passes even with a negative row.
import tempfile
import os

from persistence import open_database
from balance import ensure_non_negative

work = tempfile.mkdtemp()
db = open_database(os.path.join(work, "ledger.db"))
db.categories.create(category="OPENING", description="Opening balance")
db.accounts.create(account="CASH1", name="Till")
db.transactions.create(txn_id=1, date="2026-01-01", account="CASH1", category="OPENING", amount=500, memo="")
db.transactions.create(txn_id=2, date="2026-01-02", account="CASH1", category="OPENING", amount=-200, memo="")

ensure_non_negative(db, ["CASH1"])
assert len(db.transactions.list()) == 2
=== END AC nonneg-sums-all-transactions ===

=== AC nonneg-rejection-changes-nothing ===
Intent: A rejected check leaves every transaction row unchanged.
import tempfile
import os

from persistence import open_database
from balance import RejectedError, ensure_non_negative

work = tempfile.mkdtemp()
db = open_database(os.path.join(work, "ledger.db"))
db.categories.create(category="OPENING", description="Opening balance")
db.accounts.create(account="CASH1", name="Till")
db.transactions.create(txn_id=1, date="2026-01-01", account="CASH1", category="OPENING", amount=-500, memo="")
before = db.transactions.list()

try:
    ensure_non_negative(db, ["CASH1"])
except RejectedError:
    pass
after = db.transactions.list()
print("before:", before, "after:", after)
assert after == before
=== END AC nonneg-rejection-changes-nothing ===

## User Acceptance

- None.

## Guardrails

- The check reads only through the persistence library; it opens no database driver directly.
- Balances are computed from the database on every call; no balance is cached or stored.
- The check never converts amounts to floating point.
