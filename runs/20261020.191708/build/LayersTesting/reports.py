"""Reporting boundary; report values are derived from persisted rows."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def query_report(database: Any, query: str, parameters: tuple[object, ...] = ()) -> list[Any]:
    """Run a declared read through the persistence connection abstraction."""
    return database.query(query, parameters)


def monthly_totals(transactions: Iterable[Any]) -> list[tuple[str, int, int, int, int]]:
    """Return persisted transaction totals grouped by ascending calendar month."""
    grouped: dict[str, list[int]] = {}
    for transaction in transactions:
        month = transaction.date[:7]
        totals = grouped.setdefault(month, [0, 0, 0])
        totals[0] += 1
        if transaction.amount >= 0:
            totals[1] += transaction.amount
        else:
            totals[2] -= transaction.amount

    return [
        (month, count, inflow, outflow, inflow - outflow)
        for month, (count, inflow, outflow) in sorted(grouped.items())
    ]
