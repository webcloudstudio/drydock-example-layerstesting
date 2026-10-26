"""``ledger load accounts <csv>``: all-or-nothing load of an accounts file."""

from __future__ import annotations

from cli.errors import Rejected
from cli.loader import read_csv_rows
from cli.registry import register
from cli.validate import validate_code, validate_name


def load_accounts(db, args: list[str]) -> list[list[str]]:
    """Validate every row and rule first; write only once the whole file has passed."""
    checked: list[tuple[str, str]] = []
    seen: set[str] = set()
    for code_text, name_text in read_csv_rows(args[0], ("account", "name")):
        code = validate_code(code_text)
        name = validate_name(name_text)
        if code in seen:
            raise Rejected(f"account {code} appears more than once in the file")
        if db.accounts.get(account=code) is not None:
            raise Rejected(f"account {code} already exists")
        seen.add(code)
        checked.append((code, name))
    for code, name in checked:
        db.accounts.create(account=code, name=name)
    return [["table", "loaded"], ["accounts", str(len(checked))]]


register(("load", "accounts"), 1, 1, load_accounts)
