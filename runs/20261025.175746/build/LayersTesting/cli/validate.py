"""Input validators shared by every command. Each returns its value or raises ``Rejected``."""

from __future__ import annotations

import re
from datetime import date

from cli.errors import Rejected

CODE_PATTERN = re.compile(r"[A-Z0-9]{1,12}")
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
TXN_ID_PATTERN = re.compile(r"-?[0-9]+")
# Commas would split a CSV field and line breaks would split a row, so neither may appear in text.
FORBIDDEN_TEXT = (",", "\n", "\r")


def validate_code(text: str) -> str:
    """An account or category code: 1 to 12 characters from ``A-Z`` and ``0-9``."""
    if not CODE_PATTERN.fullmatch(text):
        raise Rejected(f"code must be 1 to 12 characters from A-Z and 0-9: {text!r}")
    return text


def validate_name(text: str) -> str:
    """A name: 1 to 40 characters, with no comma or line break."""
    return _validate_text("name", text, 1, 40)


def validate_description(text: str) -> str:
    """A category description: 1 to 40 characters, with no comma or line break."""
    return _validate_text("description", text, 1, 40)


def validate_memo(text: str) -> str:
    """A memo: 0 to 60 characters, with no comma or line break."""
    return _validate_text("memo", text, 0, 60)


def validate_txn_id(text: str) -> int:
    """A transaction id: an optionally signed run of digits, returned as an ``int``."""
    if not TXN_ID_PATTERN.fullmatch(text):
        raise Rejected(f"txn_id must be an integer: {text!r}")
    return int(text)


def validate_date(text: str) -> str:
    """A real calendar date written ``YYYY-MM-DD``."""
    if DATE_PATTERN.fullmatch(text):
        try:
            date.fromisoformat(text)
            return text
        except ValueError:
            pass
    raise Rejected(f"date must be a real calendar date as YYYY-MM-DD: {text!r}")


def _validate_text(label: str, text: str, minimum: int, maximum: int) -> str:
    if not minimum <= len(text) <= maximum:
        raise Rejected(f"{label} must be {minimum} to {maximum} characters")
    if any(mark in text for mark in FORBIDDEN_TEXT):
        raise Rejected(f"{label} must not contain a comma or line break")
    return text
