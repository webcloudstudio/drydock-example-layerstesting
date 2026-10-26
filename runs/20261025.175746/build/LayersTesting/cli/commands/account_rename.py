"""``ledger account rename <code> <name>``: change an account's name and print the updated row."""

from __future__ import annotations

from cli.balance import account_summary
from cli.errors import NotFound
from cli.output import ACCOUNT_HEADER, format_account
from cli.registry import register
from cli.validate import validate_name


def account_rename(db, args: list[str]) -> list[list[str]]:
    """Validate the name and the account before the single write; only the name changes."""
    code = args[0]
    name = validate_name(args[1])
    if db.accounts.get(account=code) is None:
        raise NotFound(f"no account {code}")
    updated = db.accounts.update(account=code, name=name)
    count, balance = account_summary(db, code)
    return [list(ACCOUNT_HEADER), format_account(updated.account, updated.name, count, balance)]


register(("account", "rename"), 2, 2, account_rename)
