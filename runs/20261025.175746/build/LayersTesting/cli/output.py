"""Standard-output CSV: comma-separated, ``\\n`` line endings, no quoting."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any

from cli.money import format_amount

TRANSACTION_HEADER = ("txn_id", "date", "account", "category", "amount", "memo")
ACCOUNT_HEADER = ("account", "name", "transactions", "balance")


def write_rows(rows: Sequence[Sequence[str]]) -> None:
    """Write each row as one CSV line to standard output. Callers pass validated fields only."""
    out = sys.stdout
    for row in rows:
        out.write(",".join(row) + "\n")


def format_account(code: str, name: str, count: int, balance: int) -> list[str]:
    """The four declared CSV fields of an account summary, with the balance as two decimals."""
    return [code, name, str(count), format_amount(balance)]


def format_transaction(row: Any) -> list[str]:
    """The six declared CSV fields of a transaction row, with the amount as two decimals."""
    return [
        str(row.txn_id),
        row.date,
        row.account,
        row.category,
        format_amount(row.amount),
        row.memo,
    ]
