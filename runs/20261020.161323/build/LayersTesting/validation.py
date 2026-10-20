"""Pure validation helpers for ledger command inputs."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation


class ValidationError(ValueError):
    """An input or business rule rejected before persistence is mutated."""


_CODE = re.compile(r"^[A-Z0-9]{1,12}$")
_MONEY = re.compile(r"^-?\d+(?:\.\d{1,2})?$")


def code(value: str, *, label: str = "code") -> str:
    if not isinstance(value, str) or not _CODE.fullmatch(value):
        raise ValidationError(f"invalid {label}")
    return value


def bounded_text(value: str, *, label: str, maximum: int, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value) or len(value) > maximum:
        raise ValidationError(f"invalid {label}")
    if "," in value or "\n" in value or "\r" in value:
        raise ValidationError(f"invalid {label}")
    return value


def name(value: str) -> str:
    return bounded_text(value, label="name", maximum=40)


def memo(value: str = "") -> str:
    return bounded_text(value, label="memo", maximum=60, allow_empty=True)


def amount_cents(value: str) -> int:
    if not isinstance(value, str) or not _MONEY.fullmatch(value):
        raise ValidationError("invalid amount")
    try:
        cents = int(Decimal(value) * 100)
    except (InvalidOperation, ValueError):
        raise ValidationError("invalid amount") from None
    if cents == 0:
        raise ValidationError("amount must be nonzero")
    return cents


def ledger_date(value: str) -> str:
    if not isinstance(value, str) or len(value) != 10:
        raise ValidationError("invalid date")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValidationError("invalid date") from None
    return value
