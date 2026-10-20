# FEATURE: Balance Rule

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Reject any command whose changes leave a touched account with a negative balance, before the transaction commits. |
| Depends On  | DATABASE.md, FEATURE-Command-Transaction.md, FEATURE-Amount-Format.md |
| Provides    | check_non_negative |
| Consumes    | transactions.list |

## Purpose

Posting, amending, deleting, transferring, and loading all end with this check. The check runs inside
the command's transaction after its changes and before commit. The module lives at `balance.py` in
the application root.

## Rules

- `check_non_negative(db, accounts)` takes the open `Database` and a list of the account codes that
  the command touched.
- For each listed account, the balance is the sum of the `amount` values of that account's
  transactions, in integer cents, computed from the rows returned by `transactions.list`.
- Any listed account whose balance is below zero causes `ValueError` to be raised.
- A balance of exactly zero is allowed.
- Accounts not in the list are not checked, even when their balance is negative.
- An empty list is accepted and performs no rejection.
- The check only reads. It never changes a row. The command layer maps the raised `ValueError` to
  exit 3 and rolls back the transaction.

## Programmatic Acceptance

=== AC balance-rejects-negative ===
Intent: A touched account whose balance falls below zero raises ValueError and leaves every row unchanged.

from persistence.testing import db_session
from balance import check_non_negative

with db_session() as db:
    db.categories.create(category="SALES", description="Sales")
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.transactions.create(txn_id=1, date="2026-01-01", account="DRAWER1", category="SALES", amount=500, memo="")
    db.transactions.create(txn_id=2, date="2026-01-02", account="DRAWER1", category="SALES", amount=-600, memo="")
    touched = ["DRAWER1"]
    before = len(db.transactions.list())
    try:
        check_non_negative(db, touched)
    except ValueError:
        raised = True
    else:
        raised = False
    after = len(db.transactions.list())
assert raised is True
assert after == before
=== END AC balance-rejects-negative ===

=== AC balance-allows-zero ===
Intent: A touched account whose balance is exactly zero does not raise.

from persistence.testing import db_session
from balance import check_non_negative

opening = 500
spend = -opening
touched = ["DRAWER1"]
with db_session() as db:
    db.categories.create(category="SALES", description="Sales")
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.transactions.create(txn_id=1, date="2026-01-01", account="DRAWER1", category="SALES", amount=opening, memo="")
    db.transactions.create(txn_id=2, date="2026-01-02", account="DRAWER1", category="SALES", amount=spend, memo="")
    ok = True
    try:
        check_non_negative(db, touched)
    except ValueError:
        ok = False
assert ok is True
=== END AC balance-allows-zero ===

=== AC balance-checks-only-touched ===
Intent: A negative account that is not in the touched list is ignored, and the same account raises when it is touched.

from persistence.testing import db_session
from balance import check_non_negative

with db_session() as db:
    db.categories.create(category="SALES", description="Sales")
    db.accounts.create(account="DRAWER1", name="Front Drawer")
    db.accounts.create(account="OTHER", name="Other Account")
    db.transactions.create(txn_id=1, date="2026-01-01", account="DRAWER1", category="SALES", amount=500, memo="")
    db.transactions.create(txn_id=2, date="2026-01-02", account="OTHER", category="SALES", amount=-100, memo="")
    untouched_ok = True
    try:
        check_non_negative(db, ["DRAWER1"])
    except ValueError:
        untouched_ok = False
    touched_raised = False
    try:
        check_non_negative(db, ["OTHER"])
    except ValueError:
        touched_raised = True
assert untouched_ok is True
assert touched_raised is True
=== END AC balance-checks-only-touched ===

=== AC balance-empty-list-accepts ===
Intent: An empty touched list performs no rejection.

from persistence.testing import db_session
from balance import check_non_negative

with db_session() as db:
    ok = True
    try:
        check_non_negative(db, [])
    except ValueError:
        ok = False
assert ok is True
=== END AC balance-empty-list-accepts ===

## User Acceptance

- None.

## Guardrails

- The balance check reads through the `persistence` package only and never imports `sqlite3` or a
  database driver.
- Balances are computed in integer cents with no floating-point arithmetic.
- The check never writes to the database.
