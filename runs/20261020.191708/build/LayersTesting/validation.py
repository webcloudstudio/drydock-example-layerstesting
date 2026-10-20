"""Pure domain validation boundary.

Validation functions in this module must complete before callers invoke persistence writes.
Money is represented as integer cents throughout the application.
"""

from __future__ import annotations

from datetime import date
import re


def validate_code(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Z0-9]{1,12}", value):
        raise ValueError("invalid code")
    return value


def validate_name(value: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 40:
        raise ValueError("invalid name")
    return value


def validate_cents(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("amount must be integer cents")
    return value


def validate_date(value: str) -> str:
    if not isinstance(value, str) or len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError("invalid date")
    date.fromisoformat(value)
    return value


def validate_memo(value: str) -> str:
    if not isinstance(value, str) or len(value) > 60:
        raise ValueError("invalid memo")
    return value
