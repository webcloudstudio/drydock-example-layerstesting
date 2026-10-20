"""Non-negative balance: a command whose changes leave an account below zero is rejected.

Pure with respect to the database: reads through the persistence library and writes nothing.
Amounts are integer cents throughout.
"""

from __future__ import annotations

from collections.abc import Iterable

from persistence import Database

__all__ = ["RejectedError", "ensure_non_negative"]

REJECTED_EXIT_CODE = 3


class RejectedError(Exception):
    """A command would leave an account balance below zero. The caller rolls the command back."""

    exit_code = REJECTED_EXIT_CODE


def ensure_non_negative(db: Database, accounts: Iterable[str]) -> None:
    """Return ``None`` when every named account's balance is zero or positive.

    The balance of an account is the sum of its transaction amounts, computed from the database on
    every call. Accounts are checked in code order and the first negative one raises
    ``RejectedError``. An account with no transactions has balance ``0``.
    """
    names = sorted(set(accounts))
    if not names:
        return
    known = {row.account for row in db.accounts.list()}
    totals: dict[str, int] = {name: 0 for name in names if name in known}
    for transaction in db.transactions.list():
        if transaction.account in totals:
            totals[transaction.account] += transaction.amount
    for name in names:
        if totals.get(name, 0) < 0:
            raise RejectedError(f"account {name} balance would be below zero")
