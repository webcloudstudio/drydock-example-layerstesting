# FEATURE: Ledger Rules

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Compute account views and projected balances, enforce the non-negative balance rule, and allocate transaction ids. |
| Depends On | DATABASE.md, FEATURE-CsvOutput.md, FEATURE-Validation.md |
| Provides | ledgerlib.rules |
| Consumes | persistence, ledgerlib.csvout |

## Purpose

`ledgerlib/rules.py` owns the business rules every write command shares: an account's transaction count and balance, the projected balance after a set of changes, the rule that no balance goes below zero, and transaction id allocation. All reads go through `db.<table>.<operation>(...)`; balances are computed in Python from list rows in integer cents.

## Interface

| Function | Behavior |
|----------|----------|
| `account_view(db, code)` | Returns an object with `account`, `name`, `transactions` (count) and `balance` (integer cents), or `None` when the account is absent. |
| `balances_after(db, changes)` | `changes` is a list of `(account_code, delta_cents)` pairs. Returns a dict mapping each affected account to its balance after every change in the list is applied. |
| `require_non_negative(db, changes)` | Raises `cli.errors.RejectedError` (exit 3) when any account in the projected result would be below zero; returns `None` otherwise. Writes nothing. |
| `next_txn_id(db)` | Returns the largest stored `txn_id` plus one, or `1` when there are no transactions. |

## Rules

- The balance check is evaluated on each account's final balance after the whole change set, not change by change, so a set that dips below zero and recovers is accepted.
- A balance of exactly zero is accepted.
- Callers read `next_txn_id` and write the row inside one database transaction so two concurrent posts never receive the same id.
- Every check happens before the caller's first write; these functions perform no writes.
- No floating point is used for money.

## Database Interface

- `FEATURE-LEDGER-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-LEDGER-013` — read: list transactions, optionally for one account - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC rules-account-view ===
Intent: The account view reports the transaction count and the integer-cent balance computed from stored rows, and an absent account yields none.

from persistence.testing import db_session
from ledgerlib import rules

acct = "ZZRLV1"
missing = "ZZRLVNONE"
cat = "ZZRLCAT1"
first = 930001
second = 930002
plus = 10000
minus = -2550
with db_session() as db:
    db.accounts.create(account=acct, name="Rules View")
    db.categories.create(category=cat, description="Rules View Cat")
    db.transactions.create(txn_id=first, date="2026-05-01", account=acct, category=cat, amount=plus, memo="a")
    db.transactions.create(txn_id=second, date="2026-05-02", account=acct, category=cat, amount=minus, memo="b")
    view = rules.account_view(db, acct)
    assert view is not None
    assert view.account == acct
    assert view.transactions == 2
    assert view.balance == plus + minus
    assert isinstance(view.balance, int)
    assert rules.account_view(db, missing) is None
=== END AC rules-account-view ===

=== AC rules-balances-after ===
Intent: The projection applies the whole change set to current balances for every affected account without writing anything.

from persistence.testing import db_session
from ledgerlib import rules

a = "ZZRLB1"
b = "ZZRLB2"
cat = "ZZRLCAT2"
start_a = 5000
start_b = 700
delta = 1200
with db_session() as db:
    db.accounts.create(account=a, name="Rules Proj A")
    db.accounts.create(account=b, name="Rules Proj B")
    db.categories.create(category=cat, description="Rules Proj Cat")
    db.transactions.create(txn_id=930011, date="2026-05-01", account=a, category=cat, amount=start_a, memo="a")
    db.transactions.create(txn_id=930012, date="2026-05-01", account=b, category=cat, amount=start_b, memo="b")
    before = len(db.transactions.list())
    result = rules.balances_after(db, [(a, -delta), (b, delta)])
    assert result[a] == start_a - delta
    assert result[b] == start_b + delta
    assert len(db.transactions.list()) == before
=== END AC rules-balances-after ===

=== AC rules-require-non-negative ===
Intent: A change set leaving any balance below zero is rejected with exit 3 while exactly zero and a recovering set are accepted, and nothing is written.

from persistence.testing import db_session
from cli.errors import RejectedError
from ledgerlib import rules

acct = "ZZRLN1"
cat = "ZZRLCAT3"
start = 5000
with db_session() as db:
    db.accounts.create(account=acct, name="Rules Neg")
    db.categories.create(category=cat, description="Rules Neg Cat")
    db.transactions.create(txn_id=930021, date="2026-05-01", account=acct, category=cat, amount=start, memo="s")
    before = len(db.transactions.list())

    assert rules.require_non_negative(db, [(acct, -start)]) is None
    assert rules.require_non_negative(db, [(acct, -8000), (acct, 4000)]) is None

    try:
        rules.require_non_negative(db, [(acct, -(start + 1))])
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("negative balance accepted")

    assert len(db.transactions.list()) == before
=== END AC rules-require-non-negative ===

=== AC rules-next-txn-id ===
Intent: The next id is the largest stored id plus one, or one for an empty table, derived here from the stored rows.

from persistence.testing import db_session
from ledgerlib import rules

acct = "ZZRLI1"
cat = "ZZRLCAT4"
high = 940500
with db_session() as db:
    db.accounts.create(account=acct, name="Rules Id")
    db.categories.create(category=cat, description="Rules Id Cat")
    existing = [t.txn_id for t in db.transactions.list()]
    expected = (max(existing) + 1) if existing else 1
    assert rules.next_txn_id(db) == expected

    db.transactions.create(txn_id=high, date="2026-05-01", account=acct, category=cat, amount=100, memo="i")
    existing = [t.txn_id for t in db.transactions.list()]
    assert rules.next_txn_id(db) == max(existing) + 1
    assert rules.next_txn_id(db) >= high + 1
=== END AC rules-next-txn-id ===

## User Acceptance

- None.

## Guardrails

- Rules never write; callers write after every check passes.
- Balances and counts are computed from stored rows at run time and never stored or hardcoded.
- No floating point is used for money.
