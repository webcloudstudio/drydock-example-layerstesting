"""``ledger report monthly``: inflow, outflow, and net per calendar month, computed from stored rows."""

from __future__ import annotations

from cli.balance import flows
from cli.money import format_amount
from cli.registry import register

MONTHLY_HEADER = ["month", "transactions", "inflow", "outflow", "net"]


def report_monthly(db, args: list[str]) -> list[list[str]]:
    """One row per month that has transactions, in ascending order, then the TOTAL row."""
    by_month: dict[str, list[int]] = {}
    for row in db.transactions.list():
        by_month.setdefault(row.date[:7], []).append(row.amount)
    rows = [list(MONTHLY_HEADER)]
    everything: list[int] = []
    for month in sorted(by_month):
        amounts = by_month[month]
        rows.append(_line(month, amounts))
        everything.extend(amounts)
    rows.append(_line("TOTAL", everything))
    return rows


def _line(label: str, amounts: list[int]) -> list[str]:
    inflow, outflow, net = flows(amounts)
    return [label, str(len(amounts)), format_amount(inflow), format_amount(outflow), format_amount(net)]


register(("report", "monthly"), 0, 0, report_monthly)
