"""Transaction rows: formatting a stored transaction for output, the next free id, and id parsing."""

import re
from typing import Union

from persistence import Database
from persistence.schema import (
    TransactionsCreateOutput,
    TransactionsGetOutput,
    TransactionsListOutput,
    TransactionsUpdateOutput,
)

from ledger_core.errors import Rejected
from ledger_core.money import format_cents

StoredTxn = Union[TransactionsCreateOutput, TransactionsGetOutput, TransactionsListOutput, TransactionsUpdateOutput]

_TXN_ID = re.compile(r"-?[0-9]+")


def parse_txn_id(text: str) -> int:
    """Parse a transaction id written as an integer. Any other text is rejected."""
    if not isinstance(text, str) or _TXN_ID.fullmatch(text) is None:
        raise Rejected(f"transaction id must be an integer: {text!r}")
    return int(text)


def txn_row(txn: StoredTxn) -> list[str]:
    """Format a stored transaction as the output row ``txn_id,date,account,category,amount,memo``."""
    return [str(txn.txn_id), txn.date, txn.account, txn.category, format_cents(txn.amount), txn.memo]


def next_txn_id(db: Database) -> int:
    """Return the largest stored ``txn_id`` plus one, or ``1`` when the ledger has no transactions."""
    return max((txn.txn_id for txn in db.transactions.list()), default=0) + 1
