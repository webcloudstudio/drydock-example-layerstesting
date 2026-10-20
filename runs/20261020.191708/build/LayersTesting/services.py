"""Application service boundary for validated, atomic ledger workflows."""

from __future__ import annotations

from collections.abc import Callable
from typing import Iterable, TypeVar

T = TypeVar("T")


def validate_before_write(validate: Callable[[], T], write: Callable[[T], object]) -> object:
    """Validate a complete operation, then perform its write plan."""
    plan = validate()
    return write(plan)


def ensure_non_negative_balances(
    transactions: Iterable[object],
    changes: Iterable[tuple[str, int]],
) -> None:
    """Reject a mutation whose resulting account balances contain a negative value.

    ``transactions`` are persisted transaction rows and ``changes`` is the complete
    delta that the caller intends to apply.  Keeping the calculation here means every
    mutation validates the same prospective state before it calls a persistence write.
    """
    balances: dict[str, int] = {}
    for transaction in transactions:
        account = getattr(transaction, "account")
        balances[account] = balances.get(account, 0) + getattr(transaction, "amount")
    for account, amount in changes:
        balances[account] = balances.get(account, 0) + amount
    if any(balance < 0 for balance in balances.values()):
        raise ValueError("negative balance")


def create_transfer(
    database: object,
    *,
    first_id: int,
    date: str,
    source: str,
    destination: str,
    category: str,
    amount: int,
) -> tuple[object, object]:
    """Create both transfer rows, compensating if the second write fails.

    The persistence contract exposes row operations rather than SQL or connection state. All
    validation, including the prospective balance check, is performed by the caller first.
    """
    transactions = getattr(database, "transactions")
    outgoing = transactions.create(
        txn_id=first_id,
        date=date,
        account=source,
        category=category,
        amount=-amount,
        memo=f"transfer to {destination}",
    )
    try:
        incoming = transactions.create(
            txn_id=first_id + 1,
            date=date,
            account=destination,
            category=category,
            amount=amount,
            memo=f"transfer from {source}",
        )
    except Exception:
        transactions.delete(txn_id=first_id)
        raise
    return outgoing, incoming
