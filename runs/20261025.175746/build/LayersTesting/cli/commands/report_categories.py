"""``ledger report categories``: inflow, outflow, and net per category, including empty categories."""

from __future__ import annotations

from cli.balance import flows
from cli.money import format_amount
from cli.registry import register

CATEGORY_HEADER = ["category", "description", "transactions", "inflow", "outflow", "net"]


def report_categories(db, args: list[str]) -> list[list[str]]:
    """One row per category in code order (zeros when unused), then the TOTAL row over all of them."""
    by_category: dict[str, list[int]] = {}
    for row in db.transactions.list():
        by_category.setdefault(row.category, []).append(row.amount)
    rows = [list(CATEGORY_HEADER)]
    everything: list[int] = []
    for category in db.categories.list():
        amounts = by_category.get(category.category, [])
        rows.append([category.category, category.description, *_figures(amounts)])
        everything.extend(amounts)
    rows.append(["TOTAL", "", *_figures(everything)])
    return rows


def _figures(amounts: list[int]) -> list[str]:
    inflow, outflow, net = flows(amounts)
    return [str(len(amounts)), format_amount(inflow), format_amount(outflow), format_amount(net)]


register(("report", "categories"), 0, 0, report_categories)
