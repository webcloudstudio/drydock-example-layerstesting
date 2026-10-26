"""``ledger account delete <code>``: remove an account that has no transactions."""

from __future__ import annotations

from cli.balance import account_summary
from cli.errors import NotFound, Rejected
from cli.registry import register


def account_delete(db, args: list[str]) -> list[list[str]]:
    """An account with stored transactions is protected; nothing is removed in that case."""
    code = args[0]
    if db.accounts.get(account=code) is None:
        raise NotFound(f"no account {code}")
    count, _ = account_summary(db, code)
    if count:
        raise Rejected(f"account {code} has {count} transactions and cannot be deleted")
    db.accounts.delete(account=code)
    return [["deleted"], [code]]


register(("account", "delete"), 1, 1, account_delete)
