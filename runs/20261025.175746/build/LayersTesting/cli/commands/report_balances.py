"""``ledger report balances``: transaction count and balance for every account, with a TOTAL row."""

from __future__ import annotations

from cli.balance import balances
from cli.money import format_amount
from cli.output import ACCOUNT_HEADER, format_account
from cli.registry import register


def report_balances(db, args: list[str]) -> list[list[str]]:
    """Accounts in code order, then TOTAL with the count and sum over every stored transaction."""
    stored = db.transactions.list()
    totals = balances(db)
    counts: dict[str, int] = {}
    for row in stored:
        counts[row.account] = counts.get(row.account, 0) + 1
    rows = [list(ACCOUNT_HEADER)]
    for account in db.accounts.list():
        rows.append(
            format_account(
                account.account,
                account.name,
                counts.get(account.account, 0),
                totals.get(account.account, 0),
            )
        )
    grand_total = sum(row.amount for row in stored)
    rows.append(["TOTAL", "", str(len(stored)), format_amount(grand_total)])
    return rows


register(("report", "balances"), 0, 0, report_balances)
