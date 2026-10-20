"""Pure validation helpers used by command services."""

from __future__ import annotations

from datetime import date
import re

_CODE = re.compile(r"^[A-Z0-9]{1,12}$")


def validate_code(value: str) -> str:
    if not value or not _CODE.fullmatch(value):
        raise ValueError("invalid code")
    return value


def validate_label(value: str) -> str:
    """Validate an account name or category description from a load file."""
    if not isinstance(value, str) or not 1 <= len(value) <= 40 or any(
        character in value for character in ",\r\n"
    ):
        raise ValueError("invalid name or description")
    return value


def validate_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid date") from exc
    return value


def validate_cents(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("amount must be integer cents")
    return value
