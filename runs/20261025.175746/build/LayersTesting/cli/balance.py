"""Account balances and the non-negative balance rule every mutating command applies before it writes.

Balances are computed from stored transaction rows in integer cents. Nothing here writes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from cli.errors import Rejected
from cli.money import format_amount


def account_summary(db, code: str) -> tuple[int, int]:
    """The stored transaction count and balance in cents of ``code``; ``(0, 0)`` when it has none."""
    rows = db.transactions.list(account=code)
    return len(rows), sum(row.amount for row in rows)


def balances(db) -> dict[str, int]:
    """Balance in cents for every account that has at least one stored transaction."""
    totals: dict[str, int] = {}
    for row in db.transactions.list():
        totals[row.account] = totals.get(row.account, 0) + row.amount
    return totals


def flows(amounts: Iterable[int]) -> tuple[int, int, int]:
    """Inflow (sum of positive amounts), outflow (sum of absolute negative amounts), and net, in cents."""
    values = list(amounts)
    inflow = sum(amount for amount in values if amount > 0)
    outflow = sum(-amount for amount in values if amount < 0)
    return inflow, outflow, inflow - outflow


def check_balances(db, deltas: Mapping[str, int]) -> None:
    """Reject (exit 3) when any account's stored balance plus its proposed change is below zero.

    ``deltas`` maps an account code to the net change in cents the command would make. A balance of
    exactly zero is allowed. Raises ``Rejected`` before anything is written; returns ``None`` otherwise.
    """
    current = balances(db)
    for account in sorted(deltas):
        after = current.get(account, 0) + deltas[account]
        if after < 0:
            raise Rejected(f"balance of {account} would be {format_amount(after)}, below zero")


def next_txn_id(db) -> int:
    """One more than the largest stored ``txn_id``, or ``1`` when no transaction is stored."""
    return max((row.txn_id for row in db.transactions.list()), default=0) + 1
