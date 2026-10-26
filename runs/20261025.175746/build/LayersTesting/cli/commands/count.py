"""``ledger count``: the number of stored rows in each table, read from the database."""

from __future__ import annotations

from cli.registry import register


def count(db, args: list[str]) -> list[list[str]]:
    """Header ``table,rows``, then accounts, categories, and transactions in that order."""
    return [
        ["table", "rows"],
        ["accounts", str(len(db.accounts.list()))],
        ["categories", str(len(db.categories.list()))],
        ["transactions", str(len(db.transactions.list()))],
    ]


register(("count",), 0, 0, count)
