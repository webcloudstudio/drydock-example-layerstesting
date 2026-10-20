"""Text validation for codes, names, descriptions, and memos. Pure checks; no database access."""

from __future__ import annotations

import re

_CODE = re.compile(r"[A-Z0-9]{1,12}")
_LINE_BREAKS = ("\n", "\r")


def check_code(text: str) -> str:
    """Return ``text`` when it is 1 to 12 characters from A-Z and 0-9; otherwise raise ``ValueError``."""
    if not _CODE.fullmatch(text):
        raise ValueError(f"code must be 1 to 12 characters from A-Z and 0-9: {text!r}")
    return text


def check_name(text: str) -> str:
    """Return ``text`` when it is 1 to 40 characters with no comma or line break; otherwise raise ``ValueError``."""
    if not 1 <= len(text) <= 40:
        raise ValueError(f"name must be 1 to 40 characters: {text!r}")
    _reject_separators(text)
    return text


def check_memo(text: str) -> str:
    """Return ``text`` when it is 0 to 60 characters with no comma or line break; otherwise raise ``ValueError``."""
    if len(text) > 60:
        raise ValueError(f"memo must be 0 to 60 characters: {text!r}")
    _reject_separators(text)
    return text


def _reject_separators(text: str) -> None:
    if "," in text:
        raise ValueError(f"comma is not allowed: {text!r}")
    if any(mark in text for mark in _LINE_BREAKS):
        raise ValueError(f"line break is not allowed: {text!r}")
