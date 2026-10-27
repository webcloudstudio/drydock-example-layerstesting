"""``ledger load`` commands: ``accounts`` and ``categories`` are all-or-nothing bulk loads.

Every row of the file is checked before the first write: the key, the text, the key's repetition
within the file, and the key's presence in the store. The rows are then inserted through
``ledger_core.atomic.run_all``, so a failing insert removes the rows already stored.

``transactions`` keeps each file ``txn_id`` and checks the foreign keys, date, amount, memo, repeats,
and the balance rule over the whole file before its first write.
"""

from collections.abc import Callable, Iterable

from cli.registry import Command
from ledger_core.atomic import run_all
from ledger_core.balances import Insert, check_no_negative
from ledger_core.csvio import read_rows
from ledger_core.errors import Operational, Rejected
from ledger_core.money import parse_amount
from ledger_core.transactions import parse_txn_id
from ledger_core.validation import validate_code, validate_date, validate_memo, validate_name

ACCOUNT_HEADER = ("account", "name")
CATEGORY_HEADER = ("category", "description")
TRANSACTION_HEADER = ("txn_id", "date", "account", "category", "amount", "memo")


def _checked_rows(
    path: str,
    header: tuple[str, str],
    validate_key: Callable[[str], str],
    stored: Iterable[str],
) -> list[tuple[str, str]]:
    """Validate every row of ``path`` before any write; return ``(key, text)`` pairs in file order."""
    already_stored = set(stored)
    seen: set[str] = set()
    checked: list[tuple[str, str]] = []
    for line, (key_text, text) in read_rows(path, header):
        try:
            key = validate_key(key_text)
            validate_name(text)
        except Rejected as exc:
            raise Rejected(f"{path} line {line}: {exc}") from exc
        if key in seen:
            raise Rejected(f"{path} line {line}: code {key} repeats within the file")
        if key in already_stored:
            raise Rejected(f"{path} line {line}: code {key} is already stored")
        seen.add(key)
        checked.append((key, text))
    return checked


def _load(
    path: str,
    header: tuple[str, str],
    table: str,
    validate_key: Callable[[str], str],
    stored: Iterable[str],
    create: Callable[[str, str], object],
    remove: Callable[[str], object],
) -> list[list[str]]:
    """Check the whole file, insert every row as one unit, and report the loaded count."""
    checked = _checked_rows(path, header, validate_key, stored)
    run_all([(_insert(create, key, text), _remove(remove, key)) for key, text in checked])
    return [["table", "loaded"], [table, str(len(checked))]]


def _insert(create: Callable[[str, str], object], key: str, text: str) -> Callable[[], object]:
    return lambda: create(key, text)


def _remove(remove: Callable[[str], object], key: str) -> Callable[[], object]:
    return lambda: remove(key)


def load_accounts(db, args: list[str]) -> list[list[str]]:
    """Load ``account,name`` rows from ``args[0]``; nothing is stored unless every row is valid."""
    return _load(
        args[0],
        ACCOUNT_HEADER,
        "accounts",
        validate_code,
        (row.account for row in db.accounts.list()),
        lambda key, name: db.accounts.create(account=key, name=name),
        lambda key: db.accounts.delete(account=key),
    )


def load_categories(db, args: list[str]) -> list[list[str]]:
    """Load ``category,description`` rows from ``args[0]``; nothing is stored unless every row is valid."""
    return _load(
        args[0],
        CATEGORY_HEADER,
        "categories",
        validate_code,
        (row.category for row in db.categories.list()),
        lambda key, text: db.categories.create(category=key, description=text),
        lambda key: db.categories.delete(category=key),
    )


TxnRow = tuple[int, str, str, str, int, str]


def _checked_transactions(db, path: str) -> list[TxnRow]:
    """Validate every row of ``path`` before any write; return ``(txn_id, date, account, category, cents, memo)``."""
    stored_ids = {txn.txn_id for txn in db.transactions.list()}
    accounts = {row.account for row in db.accounts.list()}
    categories = {row.category for row in db.categories.list()}
    seen: set[int] = set()
    checked: list[TxnRow] = []
    for line, (id_text, day, account, category, amount_text, memo) in read_rows(path, TRANSACTION_HEADER):
        try:
            txn_id = parse_txn_id(id_text)
            validate_date(day)
            cents = parse_amount(amount_text)
            validate_memo(memo)
        except Rejected as exc:
            raise Rejected(f"{path} line {line}: {exc}") from exc
        if account not in accounts:
            raise Rejected(f"{path} line {line}: account {account} does not exist")
        if category not in categories:
            raise Rejected(f"{path} line {line}: category {category} does not exist")
        if txn_id in seen:
            raise Rejected(f"{path} line {line}: transaction {txn_id} repeats within the file")
        if txn_id in stored_ids:
            raise Rejected(f"{path} line {line}: transaction {txn_id} is already stored")
        seen.add(txn_id)
        checked.append((txn_id, day, account, category, cents, memo))
    return checked


def _insert_txn(db, row: TxnRow) -> Callable[[], object]:
    txn_id, day, account, category, cents, memo = row
    return lambda: db.transactions.create(
        txn_id=txn_id, date=day, account=account, category=category, amount=cents, memo=memo
    )


def _delete_txn(db, txn_id: int) -> Callable[[], object]:
    return lambda: db.transactions.delete(txn_id=txn_id)


def load_transactions(db, args: list[str]) -> list[list[str]]:
    """Load ``txn_id,date,account,category,amount,memo`` rows from ``args[0]``; all or nothing.

    The balance rule is judged over the whole file's net effect per account, so a withdrawal listed
    before its funding deposit is accepted when the final balance is not below zero.
    """
    checked = _checked_transactions(db, args[0])
    check_no_negative(db, [Insert(account=account, amount=cents) for _, _, account, _, cents, _ in checked])
    run_all([(_insert_txn(db, row), _delete_txn(db, row[0])) for row in checked])
    return [["table", "loaded"], ["transactions", str(len(checked))]]


COMMANDS = {
    ("load", "accounts"): Command(load_accounts, 1, 1),
    ("load", "categories"): Command(load_categories, 1, 1),
    ("load", "transactions"): Command(load_transactions, 1, 1),
}
