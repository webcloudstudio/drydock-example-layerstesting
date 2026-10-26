"""``ledger txn post <account> <category> <amount> <date> [<memo>]``: store one new transaction."""

from __future__ import annotations

from cli.balance import check_balances, next_txn_id
from cli.errors import Rejected
from cli.money import parse_amount
from cli.output import TRANSACTION_HEADER, format_transaction
from cli.registry import register
from cli.validate import validate_code, validate_date, validate_memo


def txn_post(db, args: list[str]) -> list[list[str]]:
    """Every input and the resulting balance are checked before the single write."""
    account = validate_code(args[0])
    category = validate_code(args[1])
    cents = parse_amount(args[2])
    when = validate_date(args[3])
    memo = validate_memo(args[4]) if len(args) == 5 else ""
    if db.accounts.get(account=account) is None:
        raise Rejected(f"no account {account}")
    if db.categories.get(category=category) is None:
        raise Rejected(f"no category {category}")
    check_balances(db, {account: cents})
    row = db.transactions.create(
        txn_id=next_txn_id(db), date=when, account=account, category=category, amount=cents, memo=memo
    )
    return [list(TRANSACTION_HEADER), format_transaction(row)]


register(("txn", "post"), 4, 5, txn_post)
