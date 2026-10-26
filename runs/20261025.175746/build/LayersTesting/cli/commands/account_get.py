"""``ledger account get <code>``: one account row with its transaction count and balance."""

from __future__ import annotations

from cli.balance import account_summary
from cli.errors import NotFound
from cli.output import ACCOUNT_HEADER, format_account
from cli.registry import register


def account_get(db, args: list[str]) -> list[list[str]]:
    """Header row, then the account's code, name, stored transaction count, and balance."""
    code = args[0]
    row = db.accounts.get(account=code)
    if row is None:
        raise NotFound(f"no account {code}")
    count, balance = account_summary(db, code)
    return [list(ACCOUNT_HEADER), format_account(row.account, row.name, count, balance)]


register(("account", "get"), 1, 1, account_get)
