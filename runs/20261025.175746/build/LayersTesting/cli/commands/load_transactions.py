"""``ledger load transactions <csv>``: all-or-nothing load that keeps each file txn_id."""

from __future__ import annotations

from typing import Any

from cli.balance import check_balances
from cli.errors import Rejected
from cli.loader import read_csv_rows
from cli.money import parse_amount
from cli.output import TRANSACTION_HEADER
from cli.registry import register
from cli.validate import validate_code, validate_date, validate_memo, validate_txn_id
from cli.writes import store_transactions


def load_transactions(db, args: list[str]) -> list[list[str]]:
    """Validate every row, reference, and balance first; write only once the whole file has passed.

    Balances are checked on the final balance of each account after the whole file is applied
    (Decision Q-004), so a row may precede the deposit that funds it.
    """
    checked: list[dict[str, Any]] = []
    seen: set[int] = set()
    deltas: dict[str, int] = {}
    for number, fields in enumerate(read_csv_rows(args[0], TRANSACTION_HEADER), start=1):
        txn_id_text, date_text, account_text, category_text, amount_text, memo_text = fields
        row = {
            "txn_id": validate_txn_id(txn_id_text),
            "date": validate_date(date_text),
            "account": validate_code(account_text),
            "category": validate_code(category_text),
            "amount": parse_amount(amount_text),
            "memo": validate_memo(memo_text),
        }
        if row["txn_id"] in seen or db.transactions.get(txn_id=row["txn_id"]) is not None:
            raise Rejected(f"row {number}: txn_id {row['txn_id']} is repeated or already stored")
        if db.accounts.get(account=row["account"]) is None:
            raise Rejected(f"row {number}: no account {row['account']}")
        if db.categories.get(category=row["category"]) is None:
            raise Rejected(f"row {number}: no category {row['category']}")
        seen.add(row["txn_id"])
        deltas[row["account"]] = deltas.get(row["account"], 0) + row["amount"]
        checked.append(row)
    check_balances(db, deltas)
    store_transactions(db, checked)
    return [["table", "loaded"], ["transactions", str(len(checked))]]


register(("load", "transactions"), 1, 1, load_transactions)
