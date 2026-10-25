"""``ledger report``: balances, monthly totals, and category totals, each computed from the store."""

from collections import defaultdict

from cli.context import open_store
from cli.core import format_amount
from cli.registry import register
from cli.views import ACCOUNT_HEADER, account_row

MONTHLY_HEADER = ["month", "transactions", "inflow", "outflow", "net"]
CATEGORY_HEADER = ["category", "description", "transactions", "inflow", "outflow", "net"]


def balances(args: list[str]) -> list[list[str]]:
    rows = [ACCOUNT_HEADER]
    count = 0
    total = 0
    with open_store() as db:
        for account in db.accounts.list():
            txns = db.transactions.list(account=account.account)
            rows.append(account_row(account, txns))
            count += len(txns)
            total += sum(txn.amount for txn in txns)
    rows.append(["TOTAL", "", str(count), format_amount(total)])
    return rows


def monthly(args: list[str]) -> list[list[str]]:
    by_month: dict[str, list[int]] = defaultdict(list)
    with open_store() as db:
        amounts = []
        for txn in db.transactions.list():
            by_month[txn.date[:7]].append(txn.amount)
            amounts.append(txn.amount)
    rows = [MONTHLY_HEADER]
    for month in sorted(by_month):
        count, inflow, outflow = _flows(by_month[month])
        rows.append([month, str(count), format_amount(inflow), format_amount(outflow),
                     format_amount(inflow - outflow)])
    count, inflow, outflow = _flows(amounts)
    rows.append(["TOTAL", str(count), format_amount(inflow), format_amount(outflow),
                 format_amount(inflow - outflow)])
    return rows


def categories(args: list[str]) -> list[list[str]]:
    rows = [CATEGORY_HEADER]
    everything: list[int] = []
    with open_store() as db:
        for category in db.categories.list():
            amounts = [txn.amount for txn in db.transactions.list(category=category.category)]
            everything.extend(amounts)
            count, inflow, outflow = _flows(amounts)
            rows.append([category.category, category.description, str(count),
                         format_amount(inflow), format_amount(outflow),
                         format_amount(inflow - outflow)])
    count, inflow, outflow = _flows(everything)
    rows.append(["TOTAL", "", str(count), format_amount(inflow), format_amount(outflow),
                 format_amount(inflow - outflow)])
    return rows


def _flows(amounts: list[int]) -> tuple[int, int, int]:
    """Return (count, inflow, outflow) in cents; outflow is the magnitude of the debits."""
    inflow = sum(amount for amount in amounts if amount > 0)
    outflow = -sum(amount for amount in amounts if amount < 0)
    return len(amounts), inflow, outflow


register(("report", "balances"), balances, (0, 0))
register(("report", "monthly"), monthly, (0, 0))
register(("report", "categories"), categories, (0, 0))
