"""Balance rule: a proposed set of transaction changes must leave no account below zero.

An account's balance is the sum of its stored transaction amounts in integer cents. The check only
reads through the persistence interface and never writes.
"""

from dataclasses import dataclass
from typing import Union

from ledger_core.errors import NotFound, Rejected
from persistence import Database


@dataclass(frozen=True)
class Insert:
    """A transaction to be added to ``account`` with ``amount`` cents."""

    account: str
    amount: int


@dataclass(frozen=True)
class Edit:
    """A stored transaction whose amount becomes ``amount`` cents."""

    txn_id: int
    amount: int


@dataclass(frozen=True)
class Delete:
    """A stored transaction to be removed."""

    txn_id: int


Change = Union[Insert, Edit, Delete]


def current_balance(db: Database, account: str) -> int:
    """Return the sum of the stored amounts of ``account``; ``0`` when it has none."""
    return sum(row.amount for row in db.transactions.list(account=account))


def _stored(db: Database, txn_id: int):
    stored = db.transactions.get(txn_id=txn_id)
    if stored is None:
        raise NotFound(f"transaction {txn_id} does not exist")
    return stored


def _net_deltas(db: Database, changes: list[Change]) -> dict[str, int]:
    """Group the changes by account and sum each account's net effect in cents."""
    deltas: dict[str, int] = {}
    for change in changes:
        if isinstance(change, Insert):
            account, delta = change.account, change.amount
        elif isinstance(change, Edit):
            stored = _stored(db, change.txn_id)
            account, delta = stored.account, change.amount - stored.amount
        elif isinstance(change, Delete):
            stored = _stored(db, change.txn_id)
            account, delta = stored.account, -stored.amount
        else:
            raise Rejected(f"unknown transaction change: {change!r}")
        deltas[account] = deltas.get(account, 0) + delta
    return deltas


def check_no_negative(db: Database, changes: list[Change]) -> None:
    """Raise ``Rejected`` when any affected account's resulting balance is below zero.

    Changes are judged together by their net effect per account, so their order does not matter.
    A resulting balance of exactly zero is allowed. Accounts the changes do not touch are not judged.
    """
    for account, delta in _net_deltas(db, list(changes)).items():
        resulting = current_balance(db, account) + delta
        if resulting < 0:
            raise Rejected(f"account {account} would be overdrawn by {-resulting} cents")
