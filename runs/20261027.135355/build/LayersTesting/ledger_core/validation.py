"""Pure validation of codes, names, memos, and dates.

Each function returns the validated value unchanged, or raises ``Rejected``. Nothing here touches
storage or prints anything.
"""

import datetime
import re

from ledger_core.errors import Rejected

CODE_MAX = 12
NAME_MAX = 40
MEMO_MAX = 60

_CODE = re.compile(r"[A-Z0-9]{1,%d}" % CODE_MAX)
_DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_FORBIDDEN_TEXT = (",", "\n", "\r")


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise Rejected(f"{label} must be text")
    return value


def _check_length(value: str, label: str, low: int, high: int) -> None:
    if not low <= len(value) <= high:
        raise Rejected(f"{label} must be {low} to {high} characters")


def _check_plain_text(value: str, label: str) -> None:
    if any(mark in value for mark in _FORBIDDEN_TEXT):
        raise Rejected(f"{label} must not contain a comma or newline")


def validate_code(value: str) -> str:
    """Accept 1 to 12 characters, each ``A-Z`` or ``0-9``."""
    text = _require_text(value, "code")
    if not _CODE.fullmatch(text):
        raise Rejected("code must be 1 to 12 characters from A-Z and 0-9")
    return value


def validate_name(value: str) -> str:
    """Accept 1 to 40 characters with no comma or newline."""
    text = _require_text(value, "name")
    _check_length(text, "name", 1, NAME_MAX)
    _check_plain_text(text, "name")
    return value


def validate_memo(value: str) -> str:
    """Accept 0 to 60 characters with no comma or newline."""
    text = _require_text(value, "memo")
    _check_length(text, "memo", 0, MEMO_MAX)
    _check_plain_text(text, "memo")
    return value


def validate_date(value: str) -> str:
    """Accept a real calendar date written ``YYYY-MM-DD``."""
    text = _require_text(value, "date")
    match = _DATE.fullmatch(text)
    if match is None:
        raise Rejected("date must be written YYYY-MM-DD")
    year, month, day = (int(part) for part in match.groups())
    try:
        datetime.date(year, month, day)
    except ValueError as exc:
        raise Rejected(f"date is not a real calendar date: {text}") from exc
    return value
