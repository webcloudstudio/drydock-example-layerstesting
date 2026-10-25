"""``ledger txn``: post, get, delete, and amend one transaction."""

from cli.context import open_store
from cli.core import balance_guard, parse_amount, validate_code, validate_date, validate_memo
from cli.errors import NotFound, Rejected
from cli.registry import register
from cli.views import TXN_HEADER, next_txn_id, parse_txn_id, txn_row


def post_txn(args: list[str]) -> list[list[str]]:
    account, category, amount_text, day, *rest = args
    memo = rest[0] if rest else ""
    amount = parse_amount(amount_text)
    validate_date(day)
    validate_memo(memo)
    validate_code(account)
    validate_code(category)
    with open_store() as db:
        if db.accounts.get(account=account) is None:
            raise Rejected(f"no account {account}")
        if db.categories.get(category=category) is None:
            raise Rejected(f"no category {category}")
        balance_guard(db, {account: amount})
        created = db.transactions.create(
            txn_id=next_txn_id(db), date=day, account=account, category=category,
            amount=amount, memo=memo,
        )
        return [TXN_HEADER, txn_row(created)]


def get_txn(args: list[str]) -> list[list[str]]:
    (text,) = args
    txn_id = parse_txn_id(text)
    with open_store() as db:
        txn = db.transactions.get(txn_id=txn_id)
        if txn is None:
            raise NotFound(f"no transaction {txn_id}")
        return [TXN_HEADER, txn_row(txn)]


def delete_txn(args: list[str]) -> list[list[str]]:
    (text,) = args
    txn_id = parse_txn_id(text)
    with open_store() as db:
        txn = db.transactions.get(txn_id=txn_id)
        if txn is None:
            raise NotFound(f"no transaction {txn_id}")
        balance_guard(db, {txn.account: -txn.amount})
        db.transactions.delete(txn_id=txn_id)
    return [["deleted"], [str(txn_id)]]


def amend_txn(args: list[str]) -> list[list[str]]:
    text, amount_text = args
    txn_id = parse_txn_id(text)
    amount = parse_amount(amount_text)
    with open_store() as db:
        txn = db.transactions.get(txn_id=txn_id)
        if txn is None:
            raise NotFound(f"no transaction {txn_id}")
        balance_guard(db, {txn.account: amount - txn.amount})
        amended = db.transactions.update(txn_id=txn_id, amount=amount)
        return [TXN_HEADER, txn_row(amended)]


register(("txn", "post"), post_txn, (4, 5))
register(("txn", "get"), get_txn, (1, 1))
register(("txn", "delete"), delete_txn, (1, 1))
register(("txn", "amend"), amend_txn, (2, 2))
