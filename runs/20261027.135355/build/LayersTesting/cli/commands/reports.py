"""Report commands: ``ledger report balances|monthly|categories``.

Each report reads the stored rows on every run and computes its figures in integer cents. No row,
count, or total is embedded, and nothing is written to the database.
"""

from cli.registry import Command
from ledger_core.money import format_cents
from ledger_core.reports import flow_cells

BALANCES_HEADER = ["account", "name", "transactions", "balance"]
MONTHLY_HEADER = ["month", "transactions", "inflow", "outflow", "net"]
CATEGORIES_HEADER = ["category", "description", "transactions", "inflow", "outflow", "net"]


def report_balances(db, args: list[str]) -> list[list[str]]:
    """One row per account by code with its transaction count and balance, then the TOTAL row."""
    amounts_by_account: dict[str, list[int]] = {}
    all_amounts: list[int] = []
    for txn in db.transactions.list():
        amounts_by_account.setdefault(txn.account, []).append(txn.amount)
        all_amounts.append(txn.amount)
    rows = [BALANCES_HEADER]
    for account in sorted(db.accounts.list(), key=lambda row: row.account):
        mine = amounts_by_account.get(account.account, [])
        rows.append([account.account, account.name, str(len(mine)), format_cents(sum(mine))])
    rows.append(["TOTAL", "", str(len(all_amounts)), format_cents(sum(all_amounts))])
    return rows


def report_monthly(db, args: list[str]) -> list[list[str]]:
    """One row per ``YYYY-MM`` that has transactions, ascending, then the TOTAL row."""
    amounts_by_month: dict[str, list[int]] = {}
    all_amounts: list[int] = []
    for txn in db.transactions.list():
        amounts_by_month.setdefault(txn.date[:7], []).append(txn.amount)
        all_amounts.append(txn.amount)
    rows = [MONTHLY_HEADER]
    for month in sorted(amounts_by_month):
        rows.append([month, *flow_cells(amounts_by_month[month])])
    rows.append(["TOTAL", *flow_cells(all_amounts)])
    return rows


def report_categories(db, args: list[str]) -> list[list[str]]:
    """One row per category by code, including categories with no transactions, then the TOTAL row."""
    amounts_by_category: dict[str, list[int]] = {}
    all_amounts: list[int] = []
    for txn in db.transactions.list():
        amounts_by_category.setdefault(txn.category, []).append(txn.amount)
        all_amounts.append(txn.amount)
    rows = [CATEGORIES_HEADER]
    for category in sorted(db.categories.list(), key=lambda row: row.category):
        mine = amounts_by_category.get(category.category, [])
        rows.append([category.category, category.description, *flow_cells(mine)])
    rows.append(["TOTAL", "", *flow_cells(all_amounts)])
    return rows


COMMANDS = {
    ("report", "balances"): Command(report_balances, 0, 0),
    ("report", "monthly"): Command(report_monthly, 0, 0),
    ("report", "categories"): Command(report_categories, 0, 0),
}
