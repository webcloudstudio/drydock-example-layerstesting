"""``ledger init``: reset the ledger to empty. Writes nothing to standard output."""

from __future__ import annotations

from cli.registry import register


def init(db, args: list[str]) -> list[list[str]]:
    """Delete transactions first, then categories and accounts, so no foreign key is violated."""
    for row in db.transactions.list():
        db.transactions.delete(txn_id=row.txn_id)
    for row in db.categories.list():
        db.categories.delete(category=row.category)
    for row in db.accounts.list():
        db.accounts.delete(account=row.account)
    return []


register(("init",), 0, 0, init)
