"""Conversion between amount text and integer cents.

Amounts are signed integer cents everywhere. Parsing and formatting use integer arithmetic only.
"""

import re

from ledger_core.errors import Rejected

_AMOUNT = re.compile(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?")


def parse_amount(text: str) -> int:
    """Parse ``-?DIGITS[.D[D]]`` into integer cents. Zero and three or more decimals are rejected."""
    if not isinstance(text, str):
        raise Rejected("amount must be text")
    match = _AMOUNT.fullmatch(text)
    if match is None:
        raise Rejected(f"amount must look like -12.50 with at most two decimals: {text!r}")
    sign, whole, fraction = match.groups()
    cents = int(whole) * 100 + int((fraction or "").ljust(2, "0"))
    if cents == 0:
        raise Rejected("amount must not be zero")
    return -cents if sign else cents


def format_cents(cents: int) -> str:
    """Render integer cents with exactly two decimals, a leading ``-`` when negative, no separators."""
    if not isinstance(cents, int) or isinstance(cents, bool):
        raise Rejected("cents must be an integer")
    sign = "-" if cents < 0 else ""
    magnitude = abs(cents)
    return f"{sign}{magnitude // 100}.{magnitude % 100:02d}"
