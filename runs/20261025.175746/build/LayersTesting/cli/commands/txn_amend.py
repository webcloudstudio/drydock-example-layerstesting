"""``ledger txn amend <id> <amount>``: change only the amount of one stored transaction."""

from __future__ import annotations

from cli.balance import check_balances
from cli.errors import NotFound
from cli.money import parse_amount
from cli.output import TRANSACTION_HEADER, format_transaction
from cli.registry import register
from cli.validate import validate_txn_id


def txn_amend(db, args: list[str]) -> list[list[str]]:
    """The balance check uses only the change in amount; date, account, category, memo are untouched."""
    txn_id = validate_txn_id(args[0])
    cents = parse_amount(args[1])
    row = db.transactions.get(txn_id=txn_id)
    if row is None:
        raise NotFound(f"no transaction {txn_id}")
    check_balances(db, {row.account: cents - row.amount})
    updated = db.transactions.update(txn_id=txn_id, amount=cents)
    return [list(TRANSACTION_HEADER), format_transaction(updated)]


register(("txn", "amend"), 2, 2, txn_amend)
