# FEATURE: Balance Rules

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Account summaries and the non-negative balance check used by every mutating command. |
| Depends On | FEATURE-CliFoundation.md, DATABASE.md |
| Provides | cli.balance.account_summary, cli.balance.balances, cli.balance.check_balances, cli.balance.next_txn_id |
| Consumes | transactions.list, accounts.get |

## Purpose

An account's balance is the sum of its transaction amounts. No command may leave a balance below
zero. This module computes balances from stored rows in integer cents and applies the rule before a
command writes, so a violation changes nothing.

## Interface

| Function | Contract |
|---|---|
| `account_summary(db, code) -> tuple[int, int]` | Transaction count and balance in cents for the account, computed from its stored transactions; `(0, 0)` when it has none. |
| `balances(db) -> dict[str, int]` | Balance in cents per account that has transactions. |
| `check_balances(db, deltas)` | `deltas` maps account code to the net change in cents the command would make. Raises `Rejected` (exit 3) when any stored balance plus its delta is below zero; returns `None` otherwise. Writes nothing. |
| `next_txn_id(db) -> int` | One more than the largest stored `txn_id`, or `1` when the table is empty. |

Commands express a post as `{account: amount}`, an amend as `{account: new - old}`, a delete as
`{account: -amount}`, a transfer as both sides, and a load as the per-account sum of the file.
A balance of exactly zero is allowed. Computation is service-side from listed rows (decision Q-002).

## Database Interface

- `FEATURE-TRANSACTIONS-003` — read: list transactions for balances and the largest id - supplies: `account` - returns: `txn_id`, `account`, `amount`
- `FEATURE-ACCOUNTS-002` — read: confirm an account exists - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC balancerules-summary ===
Intent: account_summary returns the stored transaction count and the integer-cent sum of its amounts.

from persistence.testing import db_session
from cli.balance import account_summary

acct = "UTBAL1"
cat = "UTBALC1"
amounts = [1000, -300, 250]
with db_session() as db:
    db.accounts.create(account=acct, name="Balance Probe")
    db.categories.create(category=cat, description="Balance Category")
    for offset, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=980001 + offset, date="2026-04-01", account=acct,
            category=cat, amount=cents, memo="",
        )
    count, balance = account_summary(db, acct)
    assert count == len(amounts)
    assert balance == sum(amounts)
    assert isinstance(balance, int)
=== END AC balancerules-summary ===

=== AC balancerules-summary-empty ===
Intent: An account with no transactions has a zero count and zero balance.

from persistence.testing import db_session
from cli.balance import account_summary

acct = "UTBAL2"
with db_session() as db:
    db.accounts.create(account=acct, name="Empty Probe")
    count, balance = account_summary(db, acct)
    assert count == 0
    assert balance == 0
=== END AC balancerules-summary-empty ===

=== AC balancerules-balances ===
Intent: balances returns the per-account sums computed from stored rows.

from persistence.testing import db_session
from cli.balance import balances

acct_a = "UTBAL3A"
acct_b = "UTBAL3B"
cat = "UTBALC3"
with db_session() as db:
    db.accounts.create(account=acct_a, name="A")
    db.accounts.create(account=acct_b, name="B")
    db.categories.create(category=cat, description="Cat")
    plan = [(980011, acct_a, 500), (980012, acct_a, -200), (980013, acct_b, 75)]
    for txn_id, acct, cents in plan:
        db.transactions.create(
            txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=cents, memo=""
        )
    result = balances(db)
    assert result[acct_a] == sum(c for _, a, c in plan if a == acct_a)
    assert result[acct_b] == sum(c for _, a, c in plan if a == acct_b)
=== END AC balancerules-balances ===

=== AC balancerules-check-boundary ===
Intent: check_balances accepts a change that lands exactly on zero and rejects one cent below.

from persistence.testing import db_session
from cli.balance import check_balances
from cli.errors import Rejected

acct = "UTBAL4"
cat = "UTBALC4"
cents = 700
with db_session() as db:
    db.accounts.create(account=acct, name="Boundary")
    db.categories.create(category=cat, description="Cat")
    db.transactions.create(
        txn_id=980021, date="2026-04-03", account=acct, category=cat, amount=cents, memo=""
    )
    assert check_balances(db, {acct: -cents}) is None
    try:
        check_balances(db, {acct: -cents - 1})
    except Rejected as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("negative balance accepted")
=== END AC balancerules-check-boundary ===

=== AC balancerules-check-any-account ===
Intent: check_balances rejects when any one of several accounts would go negative.

from persistence.testing import db_session
from cli.balance import check_balances
from cli.errors import Rejected

rich = "UTBAL5R"
poor = "UTBAL5P"
cat = "UTBALC5"
with db_session() as db:
    db.accounts.create(account=rich, name="Rich")
    db.accounts.create(account=poor, name="Poor")
    db.categories.create(category=cat, description="Cat")
    db.transactions.create(
        txn_id=980031, date="2026-04-04", account=rich, category=cat, amount=10000, memo=""
    )
    db.transactions.create(
        txn_id=980032, date="2026-04-04", account=poor, category=cat, amount=100, memo=""
    )
    assert check_balances(db, {rich: -500, poor: 500}) is None
    try:
        check_balances(db, {rich: 500, poor: -101})
    except Rejected:
        pass
    else:
        raise AssertionError("negative balance accepted")
=== END AC balancerules-check-any-account ===

=== AC balancerules-check-writes-nothing ===
Intent: A rejected balance check leaves the stored transactions unchanged.

from persistence.testing import db_session
from cli.balance import check_balances
from cli.errors import Rejected

acct = "UTBAL6"
cat = "UTBALC6"
with db_session() as db:
    db.accounts.create(account=acct, name="Stable")
    db.categories.create(category=cat, description="Cat")
    db.transactions.create(
        txn_id=980041, date="2026-04-05", account=acct, category=cat, amount=100, memo=""
    )
    before = db.transactions.list(account=acct)
    try:
        check_balances(db, {acct: -1000})
    except Rejected:
        pass
    after = db.transactions.list(account=acct)
    assert after == before
=== END AC balancerules-check-writes-nothing ===

=== AC balancerules-next-id ===
Intent: next_txn_id is one more than the largest stored id, or 1 when the table is empty.

from persistence.testing import db_session
from cli.balance import next_txn_id

acct = "UTBAL7"
cat = "UTBALC7"
with db_session() as db:
    db.accounts.create(account=acct, name="Ids")
    db.categories.create(category=cat, description="Cat")
    stored = [r.txn_id for r in db.transactions.list()]
    assert next_txn_id(db) == (max(stored) + 1 if stored else 1)
    big = max(stored + [0]) + 5
    db.transactions.create(
        txn_id=big, date="2026-04-06", account=acct, category=cat, amount=10, memo=""
    )
    assert next_txn_id(db) == big + 1
=== END AC balancerules-next-id ===

## User Acceptance

- None.

## Guardrails

- Balances are computed from stored rows in integer cents; no balance, count, or id is hardcoded.
- The check never writes.
- No floating point is used for money.
