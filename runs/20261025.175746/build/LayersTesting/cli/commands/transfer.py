"""``ledger transfer <from> <to> <amount> <date>``: move cash between two accounts, both rows or neither."""

from __future__ import annotations

from cli.balance import check_balances, next_txn_id
from cli.errors import Rejected
from cli.money import parse_amount
from cli.output import TRANSACTION_HEADER, format_transaction
from cli.registry import register
from cli.validate import validate_code, validate_date
from cli.writes import store_transactions

TRANSFER_CATEGORY = "TRANSFER"


def transfer(db, args: list[str]) -> list[list[str]]:
    """Every check completes before the first write; the two rows are stored as one group."""
    source = validate_code(args[0])
    destination = validate_code(args[1])
    cents = parse_amount(args[2])
    when = validate_date(args[3])
    if cents < 0:
        raise Rejected("transfer amount must be positive")
    if source == destination:
        raise Rejected("transfer needs two different accounts")
    for code in (source, destination):
        if db.accounts.get(account=code) is None:
            raise Rejected(f"no account {code}")
    if db.categories.get(category=TRANSFER_CATEGORY) is None:
        raise Rejected(f"no category {TRANSFER_CATEGORY}")
    check_balances(db, {source: -cents, destination: cents})
    first = next_txn_id(db)
    stored = store_transactions(
        db,
        [
            {
                "txn_id": first, "date": when, "account": source, "category": TRANSFER_CATEGORY,
                "amount": -cents, "memo": f"transfer to {destination}",
            },
            {
                "txn_id": first + 1, "date": when, "account": destination, "category": TRANSFER_CATEGORY,
                "amount": cents, "memo": f"transfer from {source}",
            },
        ],
    )
    return [list(TRANSACTION_HEADER)] + [format_transaction(row) for row in stored]


register(("transfer",), 4, 4, transfer)
