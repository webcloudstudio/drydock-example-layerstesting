"""``ledger transfer``: move cash between two accounts as two TRANSFER rows."""

from cli.context import open_store
from cli.core import balance_guard, parse_amount, validate_code, validate_date
from cli.errors import OperationalError, Rejected
from cli.registry import register
from cli.views import TRANSFER_CATEGORY, TXN_HEADER, Txn, next_txn_id, txn_row


def transfer(args: list[str]) -> list[list[str]]:
    source, target, amount_text, day = args
    amount = parse_amount(amount_text)
    if amount < 0:
        raise Rejected("transfer amount must be positive")
    validate_date(day)
    validate_code(source)
    validate_code(target)
    if source == target:
        raise Rejected("transfer needs two different accounts")
    with open_store() as db:
        if db.accounts.get(account=source) is None:
            raise Rejected(f"no account {source}")
        if db.accounts.get(account=target) is None:
            raise Rejected(f"no account {target}")
        if db.categories.get(category=TRANSFER_CATEGORY) is None:
            raise OperationalError(f"category {TRANSFER_CATEGORY} is missing from the store")
        balance_guard(db, {source: -amount})
        first = next_txn_id(db)
        outgoing = Txn(first, day, source, TRANSFER_CATEGORY, -amount, f"transfer to {target}")
        incoming = Txn(first + 1, day, target, TRANSFER_CATEGORY, amount, f"transfer from {source}")
        db.transactions.create(**outgoing._asdict())
        db.transactions.create(**incoming._asdict())
    return [TXN_HEADER, txn_row(outgoing), txn_row(incoming)]


register(("transfer",), transfer, (4, 4))
