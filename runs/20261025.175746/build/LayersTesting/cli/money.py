"""Money as integer cents. Text is parsed and formatted with integer arithmetic only."""

from __future__ import annotations

import re

from cli.errors import Rejected

AMOUNT_PATTERN = re.compile(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?")


def parse_amount(text: str) -> int:
    """Parse ``-?DIGITS[.D[D]]`` into integer cents. Zero and any other shape are rejected."""
    match = AMOUNT_PATTERN.fullmatch(text)
    if match is None:
        raise Rejected(f"amount must look like 12.50 or -3.1, with at most two decimals: {text!r}")
    sign, whole, fraction = match.groups()
    cents = int(whole) * 100 + int((fraction or "").ljust(2, "0"))
    if cents == 0:
        raise Rejected("amount must not be zero")
    return -cents if sign else cents


def format_amount(cents: int) -> str:
    """Format integer cents as a two-decimal amount with a leading ``-`` when negative."""
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole}.{fraction:02d}"
