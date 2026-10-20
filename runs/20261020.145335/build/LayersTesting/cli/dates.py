"""Calendar date validation. Accepts only real calendar dates written YYYY-MM-DD."""

from __future__ import annotations

import re
from datetime import date

_SHAPE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def check_date(text: str) -> str:
    """Return ``text`` when it is a real calendar date in YYYY-MM-DD form; otherwise raise ``ValueError``."""
    if not _SHAPE.fullmatch(text):
        raise ValueError(f"date must be written YYYY-MM-DD: {text!r}")
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"not a calendar date: {text!r}") from exc
    return text
