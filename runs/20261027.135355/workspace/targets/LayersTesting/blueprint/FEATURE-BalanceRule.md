# FEATURE: Balance Rule

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Checks that a proposed set of transaction changes leaves no account balance below zero before anything is written. |
| Depends On | ARCHITECTURE.md, DATABASE.md |
| Provides | ledger_core.balances |
| Consumes | persistence.transactions |

## Purpose

An account's balance is the sum of its transaction amounts in integer cents. Load, post, amend, delete, and transfer call this module before their first write. It only reads and never writes.

## Interface

`ledger_core.balances`:

| Name | Meaning |
|---|---|
| `Insert(account, amount)` | A transaction to be added to `account` with `amount` cents. |
| `Edit(txn_id, amount)` | A stored transaction whose amount becomes `amount`. |
| `Delete(txn_id)` | A stored transaction to be removed. |
| `current_balance(db, account) -> int` | Sum of the stored amounts of `account`; `0` when it has none. |
| `check_no_negative(db, changes)` | Raises `Rejected` (exit 3) if any affected account's resulting balance is below zero; returns `None` otherwise. |

`check_no_negative` groups all changes by account, takes each account's stored balance, applies the combined net delta (an `Edit` contributes new minus stored amount, a `Delete` contributes minus the stored amount), and rejects when any result is below zero. Changes are judged together, not one after another, so the order of changes does not matter. A resulting balance of exactly zero is allowed.

## Database Interface

- `FEATURE-TXN-002` — read: get a stored transaction for an edit or delete - supplies: `txn_id` - returns: `account`, `amount`
- `FEATURE-TXN-005` — read: list an account's transactions to sum its balance - supplies: — - returns: `amount`

## Programmatic Acceptance

=== AC balance-current ===
Intent: current_balance sums an account's stored amounts and is zero for an account with no transactions.

from persistence.testing import db_session
from ledger_core.balances import current_balance

acct, empty, cat = "ZZBR1", "ZZBR2", "ZZBRC1"
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Probe")
    db.accounts.create(account=empty, name="Empty Probe")
    db.categories.create(category=cat, description="Balance Cat")
    amounts = [1000, -300]
    for offset, cents in enumerate(amounts):
        db.transactions.create(txn_id=900100001 + offset, date="2026-05-01", account=acct,
                               category=cat, amount=cents, memo="")
    assert current_balance(db, acct) == sum(amounts)
    assert current_balance(db, empty) == 0
=== END AC balance-current ===

=== AC balance-insert ===
Intent: An insert that lands the balance at zero passes, one cent below zero is rejected with exit 3, and nothing is written either way.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Insert
from ledger_core.errors import Rejected

acct, cat = "ZZBR3", "ZZBRC3"
with db_session() as db:
    db.accounts.create(account=acct, name="Insert Probe")
    db.categories.create(category=cat, description="Balance Cat")
    db.transactions.create(txn_id=900100011, date="2026-05-01", account=acct, category=cat, amount=700, memo="")
    before = len(db.transactions.list(account=acct))
    assert check_no_negative(db, [Insert(acct, -700)]) is None
    raised = None
    try:
        check_no_negative(db, [Insert(acct, -701)])
    except Rejected as err:
        raised = err
    assert raised is not None
    assert raised.exit_code == 3
    assert len(db.transactions.list(account=acct)) == before
=== END AC balance-insert ===

=== AC balance-insert-new-account ===
Intent: An account with no transactions accepts a positive insert and rejects a negative one.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Insert
from ledger_core.errors import Rejected

acct = "ZZBR4"
with db_session() as db:
    db.accounts.create(account=acct, name="Fresh Probe")
    assert check_no_negative(db, [Insert(acct, 500)]) is None
    raised = False
    try:
        check_no_negative(db, [Insert(acct, -1)])
    except Rejected:
        raised = True
    assert raised
=== END AC balance-insert-new-account ===

=== AC balance-edit ===
Intent: Editing the larger credit below what the debits need is rejected; editing it to exactly cover them passes.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Edit
from ledger_core.errors import Rejected

acct, cat = "ZZBR5", "ZZBRC5"
credit, debit = 900100021, 900100022
with db_session() as db:
    db.accounts.create(account=acct, name="Edit Probe")
    db.categories.create(category=cat, description="Balance Cat")
    db.transactions.create(txn_id=credit, date="2026-05-01", account=acct, category=cat, amount=1000, memo="")
    db.transactions.create(txn_id=debit, date="2026-05-02", account=acct, category=cat, amount=-300, memo="")
    assert check_no_negative(db, [Edit(credit, 300)]) is None
    raised = None
    try:
        check_no_negative(db, [Edit(credit, 299)])
    except Rejected as err:
        raised = err
    assert raised is not None
    assert raised.exit_code == 3
    stored = db.transactions.get(txn_id=credit)
    amount = stored["amount"] if isinstance(stored, dict) else stored.amount
    assert amount == 1000
=== END AC balance-edit ===

=== AC balance-delete ===
Intent: Deleting the credit that funds a debit is rejected; deleting the debit passes.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Delete
from ledger_core.errors import Rejected

acct, cat = "ZZBR6", "ZZBRC6"
credit, debit = 900100031, 900100032
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Probe")
    db.categories.create(category=cat, description="Balance Cat")
    db.transactions.create(txn_id=credit, date="2026-05-01", account=acct, category=cat, amount=1000, memo="")
    db.transactions.create(txn_id=debit, date="2026-05-02", account=acct, category=cat, amount=-300, memo="")
    assert check_no_negative(db, [Delete(debit)]) is None
    raised = None
    try:
        check_no_negative(db, [Delete(credit)])
    except Rejected as err:
        raised = err
    assert raised is not None
    assert raised.exit_code == 3
    assert db.transactions.get(txn_id=credit) is not None
=== END AC balance-delete ===

=== AC balance-combined ===
Intent: Several changes to one account are judged by their net effect regardless of order; a credit and a debit that net to a non-negative balance pass in either order.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Insert
from ledger_core.errors import Rejected

acct, cat = "ZZBR7", "ZZBRC7"
with db_session() as db:
    db.accounts.create(account=acct, name="Combined Probe")
    db.categories.create(category=cat, description="Balance Cat")
    db.transactions.create(txn_id=900100041, date="2026-05-01", account=acct, category=cat, amount=700, memo="")
    credit, debit = Insert(acct, 500), Insert(acct, -1100)
    assert check_no_negative(db, [credit, debit]) is None
    assert check_no_negative(db, [debit, credit]) is None
    over = Insert(acct, -1300)
    raised = False
    try:
        check_no_negative(db, [credit, over])
    except Rejected:
        raised = True
    assert raised
=== END AC balance-combined ===

=== AC balance-multi-account ===
Intent: When one of several affected accounts would go negative the whole set is rejected and nothing is written.

from persistence.testing import db_session
from ledger_core.balances import check_no_negative, Insert
from ledger_core.errors import Rejected

good, poor, cat = "ZZBR8", "ZZBR9", "ZZBRC8"
with db_session() as db:
    db.accounts.create(account=good, name="Rich Probe")
    db.accounts.create(account=poor, name="Poor Probe")
    db.categories.create(category=cat, description="Balance Cat")
    db.transactions.create(txn_id=900100051, date="2026-05-01", account=good, category=cat, amount=900, memo="")
    db.transactions.create(txn_id=900100052, date="2026-05-01", account=poor, category=cat, amount=100, memo="")
    before = len(db.transactions.list(account=good)) + len(db.transactions.list(account=poor))
    raised = None
    try:
        check_no_negative(db, [Insert(good, -900), Insert(poor, -101)])
    except Rejected as err:
        raised = err
    assert raised is not None
    assert raised.exit_code == 3
    after = len(db.transactions.list(account=good)) + len(db.transactions.list(account=poor))
    assert after == before
=== END AC balance-multi-account ===

## User Acceptance

- None.

## Guardrails

- The check writes nothing; it only reads through the declared repository operations.
- Amounts are integer cents; no floating point is used.
- Only accounts touched by the proposed changes are judged; other accounts' balances do not affect the result.
- Balances are computed from stored rows, never cached or hardcoded.
