"""``ledger account add <code> <name>``: validate and store one new cash account."""

from __future__ import annotations

from cli.balance import account_summary
from cli.errors import Rejected
from cli.output import ACCOUNT_HEADER, format_account
from cli.registry import register
from cli.validate import validate_code, validate_name


def account_add(db, args: list[str]) -> list[list[str]]:
    """Every check completes before the single write; a duplicate code is refused."""
    code = validate_code(args[0])
    name = validate_name(args[1])
    if db.accounts.get(account=code) is not None:
        raise Rejected(f"account {code} already exists")
    db.accounts.create(account=code, name=name)
    count, balance = account_summary(db, code)
    return [list(ACCOUNT_HEADER), format_account(code, name, count, balance)]


register(("account", "add"), 2, 2, account_add)
