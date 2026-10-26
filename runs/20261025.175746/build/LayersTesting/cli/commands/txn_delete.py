"""``ledger txn delete <id>``: remove one stored transaction unless it leaves a negative balance."""

from __future__ import annotations

from cli.balance import check_balances
from cli.errors import NotFound
from cli.registry import register
from cli.validate import validate_txn_id


def txn_delete(db, args: list[str]) -> list[list[str]]:
    """The balance check runs with the row removed; a rejected delete keeps the row."""
    txn_id = validate_txn_id(args[0])
    row = db.transactions.get(txn_id=txn_id)
    if row is None:
        raise NotFound(f"no transaction {txn_id}")
    check_balances(db, {row.account: -row.amount})
    db.transactions.delete(txn_id=txn_id)
    return [["deleted"], [str(txn_id)]]


register(("txn", "delete"), 1, 1, txn_delete)
