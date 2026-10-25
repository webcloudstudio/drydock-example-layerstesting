"""``ledger count``: the row count of each ledger table, read from the store on every call."""

from cli.context import open_store
from cli.registry import register


def count(args: list[str]) -> list[list[str]]:
    with open_store() as db:
        return [
            ["table", "rows"],
            ["accounts", str(len(db.accounts.list()))],
            ["categories", str(len(db.categories.list()))],
            ["transactions", str(len(db.transactions.list()))],
        ]


register(("count",), count, (0, 0))
