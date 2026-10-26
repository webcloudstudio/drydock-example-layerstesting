# FEATURE: Balance Rules

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Judge every affected account balance on the final state of a command and reject any negative balance before a write. |
| Depends On | DATABASE.md, FEATURE-ErrorContract.md |
| Provides | balance_rules.check_final_balances |
| Consumes | persistence.open_database, ledger_errors.Rejected |

## Purpose

Rule 2 of the source says no command leaves an account balance below zero. Every command that
writes transactions (load, post, amend, delete, transfer) calls this one check before its first
write. An account's balance is the sum of its stored transaction amounts in integer cents.

## Interface

Module `balance_rules`, importable from the application root.

`check_final_balances(db, inserts=(), amount_changes=(), deletions=())` returns `None` or raises
`ledger_errors.Rejected`.

| Argument | Meaning |
|----------|---------|
| `db` | An open persistence `Database` (from `open_database` or `db_session`). |
| `inserts` | Iterable of `(account, amount_cents)` pending new rows. |
| `amount_changes` | Iterable of `(txn_id, new_amount_cents)` replacing a stored row's amount. |
| `deletions` | Iterable of `txn_id` of stored rows to be removed. |

## Rules

- Read stored rows only through `db.transactions.list(account=...)` and `db.transactions.get(txn_id=...)`.
- For each account touched by any pending change, compute `stored sum + pending inserts + amount deltas - deleted amounts`, in Python `int` cents. No floating point.
- Judge only the final state after all pending changes. An intermediate dip that a later pending change restores is allowed, whatever the order of the arguments.
- If any touched account's final balance is below zero, raise `Rejected`. A balance of exactly zero is allowed.
- The check performs no write of any kind.
- A `txn_id` in `amount_changes` or `deletions` that is not stored is ignored here; the calling command reports it as not found before calling this check.
- The message of `Rejected` never contains a DSN or credential.

## Database Interface

- `FEATURE-TXN-003` — read: list a transaction set by account - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-002` — read: get a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC balance-rejects-negative-insert ===
Intent: A pending insert that leaves an account below zero raises Rejected and writes nothing.

from persistence.testing import db_session
from balance_rules import check_final_balances
from ledger_errors import Rejected

acct = "ZQBR01"
cat = "ZQBRC01"
with db_session() as db:
    db.accounts.create(account=acct, name="Balance One")
    db.categories.create(category=cat, description="Balance One")
    before = len(db.transactions.list())
    try:
        check_final_balances(db, inserts=[(acct, -100)])
    except Rejected:
        pass
    else:
        raise AssertionError("expected Rejected")
    assert len(db.transactions.list()) == before
=== END AC balance-rejects-negative-insert ===

=== AC balance-final-state-only ===
Intent: An intermediate dip restored later in the same command is allowed; zero is allowed.

from persistence.testing import db_session
from balance_rules import check_final_balances

acct = "ZQBR02"
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Two")
    check_final_balances(db, inserts=[(acct, -500), (acct, 1000)])
    check_final_balances(db, inserts=[(acct, 700), (acct, -700)])
=== END AC balance-final-state-only ===

=== AC balance-amend ===
Intent: An amount change that drives the stored balance below zero is rejected, a safe one is accepted.

from persistence.testing import db_session
from balance_rules import check_final_balances
from ledger_errors import Rejected

acct = "ZQBR03"
cat = "ZQBRC03"
txn_id = 910002
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Three")
    db.categories.create(category=cat, description="Balance Three")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo=""
    )
    check_final_balances(db, amount_changes=[(txn_id, 1)])
    try:
        check_final_balances(db, amount_changes=[(txn_id, -1)])
    except Rejected:
        pass
    else:
        raise AssertionError("expected Rejected")
    assert db.transactions.get(txn_id=txn_id).amount == 1000
=== END AC balance-amend ===

=== AC balance-delete ===
Intent: Deleting a credit that funds a debit is rejected; deleting the debit is accepted.

from persistence.testing import db_session
from balance_rules import check_final_balances
from ledger_errors import Rejected

acct = "ZQBR04"
cat = "ZQBRC04"
credit_id = 910003
debit_id = 910004
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Four")
    db.categories.create(category=cat, description="Balance Four")
    db.transactions.create(
        txn_id=credit_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo=""
    )
    db.transactions.create(
        txn_id=debit_id, date="2026-04-02", account=acct, category=cat, amount=-400, memo=""
    )
    check_final_balances(db, deletions=[debit_id])
    try:
        check_final_balances(db, deletions=[credit_id])
    except Rejected:
        pass
    else:
        raise AssertionError("expected Rejected")
    assert db.transactions.get(txn_id=credit_id) is not None
    assert db.transactions.get(txn_id=debit_id) is not None
=== END AC balance-delete ===

## User Acceptance

- None.

## Guardrails

- Integer cents only; no floating point at any layer.
- The check never writes to the database.
- Diagnostics never echo a DSN, path credential or password.
