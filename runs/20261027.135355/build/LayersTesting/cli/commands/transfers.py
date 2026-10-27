"""Transfer command: ``ledger transfer <from> <to> <amount> <date>``, two linked rows stored together."""

from functools import partial

from cli.registry import Command
from ledger_core.atomic import run_all
from ledger_core.balances import Insert, check_no_negative
from ledger_core.errors import Rejected
from ledger_core.money import parse_amount
from ledger_core.transactions import next_txn_id, txn_row
from ledger_core.validation import validate_date

TRANSFER_CATEGORY = "TRANSFER"
TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


def transfer(db, args: list[str]) -> list[list[str]]:
    """Move cash between two accounts as an outgoing and an incoming row, or store neither.

    Every check, including the source balance after the debit, runs before the first insert.
    """
    source, target = args[0], args[1]
    cents = parse_amount(args[2])
    if cents < 0:
        raise Rejected("transfer amount must be positive")
    day = validate_date(args[3])
    if source == target:
        raise Rejected("transfer needs two different accounts")
    if db.accounts.get(account=source) is None:
        raise Rejected(f"account {source} does not exist")
    if db.accounts.get(account=target) is None:
        raise Rejected(f"account {target} does not exist")
    if db.categories.get(category=TRANSFER_CATEGORY) is None:
        raise Rejected(f"category {TRANSFER_CATEGORY} does not exist")
    check_no_negative(db, [Insert(account=source, amount=-cents)])

    first_id = next_txn_id(db)
    outgoing = {
        "txn_id": first_id,
        "date": day,
        "account": source,
        "category": TRANSFER_CATEGORY,
        "amount": -cents,
        "memo": f"transfer to {target}",
    }
    incoming = {
        "txn_id": first_id + 1,
        "date": day,
        "account": target,
        "category": TRANSFER_CATEGORY,
        "amount": cents,
        "memo": f"transfer from {source}",
    }
    stored = []

    def insert(fields: dict):
        stored.append(db.transactions.create(**fields))

    run_all(
        [
            (partial(insert, outgoing), partial(db.transactions.delete, txn_id=outgoing["txn_id"])),
            (partial(insert, incoming), partial(db.transactions.delete, txn_id=incoming["txn_id"])),
        ]
    )
    return [TXN_HEADER] + [txn_row(txn) for txn in stored]


COMMANDS = {
    ("transfer",): Command(transfer, 4, 4),
}
