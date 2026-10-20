"""Amount validation. Parses input text to integer cents and formats stored cents as two-decimal text. No floating point."""

from __future__ import annotations

import re

_SHAPE = re.compile(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?")


def parse_amount(text: str) -> int:
    """Return the signed integer cents for ``text``; raise ``ValueError`` unless it is ``-?DIGITS[.D[D]]`` and non-zero."""
    match = _SHAPE.fullmatch(text)
    if match is None:
        raise ValueError(f"amount must be written -?DIGITS[.D[D]]: {text!r}")
    sign, whole, fraction = match.groups()
    cents = int(whole) * 100 + int((fraction or "0").ljust(2, "0"))
    if cents == 0:
        raise ValueError(f"amount must not be zero: {text!r}")
    return -cents if sign else cents


def format_amount(cents: int) -> str:
    """Return ``cents`` as text with exactly two decimal places, a leading ``-`` when negative, and no separators."""
    whole, fraction = divmod(abs(cents), 100)
    sign = "-" if cents < 0 else ""
    return f"{sign}{whole}.{fraction:02d}"
