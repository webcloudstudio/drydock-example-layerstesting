"""``ledger txn get <id>``: print one stored transaction row."""

from __future__ import annotations

from cli.errors import NotFound
from cli.output import TRANSACTION_HEADER, format_transaction
from cli.registry import register
from cli.validate import validate_txn_id


def txn_get(db, args: list[str]) -> list[list[str]]:
    """Header row, then the stored row with its amount as two decimals. Read-only."""
    txn_id = validate_txn_id(args[0])
    row = db.transactions.get(txn_id=txn_id)
    if row is None:
        raise NotFound(f"no transaction {txn_id}")
    return [list(TRANSACTION_HEADER), format_transaction(row)]


register(("txn", "get"), 1, 1, txn_get)
