"""Report arithmetic: transaction counts and cash flows computed in integer cents.

Pure functions over amounts in cents. Nothing here touches storage or prints anything.
"""

from collections.abc import Iterable

from ledger_core.money import format_cents


def flows(amounts: Iterable[int]) -> tuple[int, int, int, int]:
    """Return ``(count, inflow, outflow, net)`` in cents.

    ``inflow`` is the sum of positive amounts, ``outflow`` the sum of the magnitudes of negative
    amounts (written positive), and ``net`` is ``inflow - outflow``. No amounts gives all zeros.
    """
    values = list(amounts)
    inflow = sum(value for value in values if value > 0)
    outflow = sum(-value for value in values if value < 0)
    return len(values), inflow, outflow, inflow - outflow


def flow_cells(amounts: Iterable[int]) -> list[str]:
    """Return the report cells ``[transactions, inflow, outflow, net]`` for ``amounts``, formatted."""
    count, inflow, outflow, net = flows(amounts)
    return [str(count), format_cents(inflow), format_cents(outflow), format_cents(net)]
