"""Transaction commands: ``ledger txn post|get|delete|amend``."""

from cli.registry import Command
from ledger_core.balances import Delete, Edit, Insert, check_no_negative
from ledger_core.errors import NotFound, Rejected
from ledger_core.money import parse_amount
from ledger_core.transactions import next_txn_id, parse_txn_id, txn_row
from ledger_core.validation import validate_date, validate_memo

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
DELETED_HEADER = ["deleted"]


def txn_post(db, args: list[str]) -> list[list[str]]:
    """Check every input and the balance rule, then insert one transaction and print its row.

    All checks run before the insert, so a rejected post stores nothing.
    """
    account, category = args[0], args[1]
    cents = parse_amount(args[2])
    day = validate_date(args[3])
    memo = validate_memo(args[4] if len(args) == 5 else "")
    if db.accounts.get(account=account) is None:
        raise Rejected(f"account {account} does not exist")
    if db.categories.get(category=category) is None:
        raise Rejected(f"category {category} does not exist")
    check_no_negative(db, [Insert(account=account, amount=cents)])
    txn = db.transactions.create(
        txn_id=next_txn_id(db), date=day, account=account, category=category, amount=cents, memo=memo
    )
    return [TXN_HEADER, txn_row(txn)]


def txn_get(db, args: list[str]) -> list[list[str]]:
    """Print one stored transaction. Read-only; a non-integer id exits 3 and an absent id exits 4."""
    txn_id = parse_txn_id(args[0])
    txn = db.transactions.get(txn_id=txn_id)
    if txn is None:
        raise NotFound(f"transaction {txn_id} does not exist")
    return [TXN_HEADER, txn_row(txn)]


def txn_delete(db, args: list[str]) -> list[list[str]]:
    """Remove a transaction unless its account balance would go below zero without it."""
    txn_id = parse_txn_id(args[0])
    if db.transactions.get(txn_id=txn_id) is None:
        raise NotFound(f"transaction {txn_id} does not exist")
    check_no_negative(db, [Delete(txn_id=txn_id)])
    db.transactions.delete(txn_id=txn_id)
    return [DELETED_HEADER, [str(txn_id)]]


def txn_amend(db, args: list[str]) -> list[list[str]]:
    """Change only the amount of a transaction, and only when its account stays at or above zero."""
    txn_id = parse_txn_id(args[0])
    cents = parse_amount(args[1])
    if db.transactions.get(txn_id=txn_id) is None:
        raise NotFound(f"transaction {txn_id} does not exist")
    check_no_negative(db, [Edit(txn_id=txn_id, amount=cents)])
    txn = db.transactions.update(txn_id=txn_id, amount=cents)
    return [TXN_HEADER, txn_row(txn)]


COMMANDS = {
    ("txn", "post"): Command(txn_post, 4, 5),
    ("txn", "get"): Command(txn_get, 1, 1),
    ("txn", "delete"): Command(txn_delete, 1, 1),
    ("txn", "amend"): Command(txn_amend, 2, 2),
}
