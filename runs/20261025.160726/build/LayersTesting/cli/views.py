"""Output shapes, id parsing, and row builders shared by the command modules.

Commands build their rows here so every table prints the same way. Nothing in this module reads
or writes the store except ``next_txn_id``, which only reads.
"""

import re
from typing import NamedTuple

from persistence import Database

from cli.core import format_amount
from cli.errors import Rejected, UsageError

ACCOUNT_COLUMNS = ["account", "name"]
CATEGORY_COLUMNS = ["category", "description"]
TXN_COLUMNS = ["txn_id", "date", "account", "category", "amount", "memo"]
ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]
TXN_HEADER = TXN_COLUMNS
LOADED_HEADER = ["table", "loaded"]
TRANSFER_CATEGORY = "TRANSFER"

#: The largest id the transactions table holds (INTEGER on PostgreSQL). A file id must fit it.
TXN_ID_MAX = 2**31 - 1

_ID_TEXT = re.compile(r"-?[0-9]+")
_LOADED_ID = re.compile(r"[0-9]+")


class Txn(NamedTuple):
    """One transaction ready to store, in the column order of the transactions table."""

    txn_id: int
    date: str
    account: str
    category: str
    amount: int
    memo: str


def parse_txn_id(text: str) -> int:
    """Return a transaction id argument. Anything but a base-10 integer is a usage error."""
    if _ID_TEXT.fullmatch(text) is None:
        raise UsageError(f"transaction id must be an integer: {text!r}")
    return int(text)


def load_txn_id(text: str) -> int:
    """Return a transaction id read from a file: a positive integer that fits the column."""
    if _LOADED_ID.fullmatch(text) is None or not 1 <= int(text) <= TXN_ID_MAX:
        raise Rejected(f"txn_id must be a positive integer up to {TXN_ID_MAX}: {text!r}")
    return int(text)


def next_txn_id(db: Database) -> int:
    """One more than the largest stored transaction id, or 1 when the table is empty."""
    return max((txn.txn_id for txn in db.transactions.list()), default=0) + 1


def txn_row(txn) -> list[str]:
    """Print one transaction in the transaction CSV shape, amount in two-decimal text."""
    return [
        str(txn.txn_id),
        txn.date,
        txn.account,
        txn.category,
        format_amount(txn.amount),
        txn.memo,
    ]


def account_row(account, txns) -> list[str]:
    """Print one account with its transaction count and balance computed from ``txns``."""
    balance = sum(txn.amount for txn in txns)
    return [account.account, account.name, str(len(txns)), format_amount(balance)]
