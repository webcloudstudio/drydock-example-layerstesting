"""Shared input rules: integer-cent amounts, field and date validators, and the projected-balance guard.

Every command takes its input through these functions so no command repeats or contradicts them.
Validators and the guard raise ``Rejected`` and never write to the store.
"""

import datetime
import re
from collections.abc import Mapping

from persistence import Database

from cli.errors import Rejected

_AMOUNT = re.compile(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?")
_CODE = re.compile(r"[A-Z0-9]{1,12}")
_DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_FORBIDDEN_TEXT = (",", "\n", "\r")


def parse_amount(text: str) -> int:
    """Return ``text`` as integer cents. Accepts ``-?DIGITS[.D[D]]`` only; zero is rejected."""
    match = _AMOUNT.fullmatch(text)
    if match is None:
        raise Rejected(f"amount must look like 12.50 or -3: {text!r}")
    sign, whole, fraction = match.groups()
    cents = int(whole) * 100 + int((fraction or "").ljust(2, "0"))
    if cents == 0:
        raise Rejected("amount must not be zero")
    return -cents if sign else cents


def format_amount(cents: int) -> str:
    """Return ``cents`` with exactly two decimals, a leading minus when negative, and no separators."""
    sign = "-" if cents < 0 else ""
    magnitude = abs(cents)
    return f"{sign}{magnitude // 100}.{magnitude % 100:02d}"


def validate_code(text: str) -> str:
    """Return ``text`` if it is 1 to 12 characters from ``A-Z`` and ``0-9``."""
    if _CODE.fullmatch(text) is None:
        raise Rejected(f"code must be 1 to 12 characters of A-Z or 0-9: {text!r}")
    return text


def validate_text(text: str, min_len: int, max_len: int) -> str:
    """Return ``text`` if its length is within bounds and it holds no comma or line break."""
    if not min_len <= len(text) <= max_len:
        raise Rejected(f"text must be {min_len} to {max_len} characters: {text!r}")
    if any(mark in text for mark in _FORBIDDEN_TEXT):
        raise Rejected("text must not contain a comma or line break")
    return text


def validate_name(text: str) -> str:
    """Return an account name or category description: 1 to 40 characters."""
    return validate_text(text, 1, 40)


def validate_memo(text: str) -> str:
    """Return a transaction memo: 0 to 60 characters."""
    return validate_text(text, 0, 60)


def validate_date(text: str) -> str:
    """Return ``text`` if it is a real calendar date written as ``YYYY-MM-DD``."""
    match = _DATE.fullmatch(text)
    if match is None:
        raise Rejected(f"date must look like 2026-04-01: {text!r}")
    year, month, day = (int(part) for part in match.groups())
    try:
        datetime.date(year, month, day)
    except ValueError as exc:
        raise Rejected(f"not a real calendar date: {text!r}") from exc
    return text


def account_balance(db: Database, account: str) -> int:
    """Return the sum of an account's transaction amounts in cents; zero when it has none."""
    return sum(row.amount for row in db.transactions.list(account=account))


def balance_guard(db: Database, deltas: Mapping[str, int]) -> None:
    """Reject the change set if any account's balance after its delta would go below zero.

    ``deltas`` maps account code to a net change in cents. Nothing is written.
    """
    for account in sorted(deltas):
        resulting = account_balance(db, account) + deltas[account]
        if resulting < 0:
            raise Rejected(
                f"account {account} would be {format_amount(resulting)}; balance may not go negative"
            )
