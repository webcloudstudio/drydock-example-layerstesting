"""Validation of codes, names, memos, and dates: accepted values return unchanged, others raise Rejected."""

import pytest

from ledger_core.errors import Rejected
from ledger_core.validation import validate_code, validate_date, validate_memo, validate_name


@pytest.mark.parametrize("value", ["DRAWER1", "A", "0", "ABCDEFGHIJKL", "Z9Z9Z9Z9Z9Z9"])
def test_code_accepts_valid_value_unchanged(value):
    assert validate_code(value) == value


@pytest.mark.parametrize("value", ["", "drawer1", "Drawer", "ABCDEFGHIJKLM", "AB-C", "A B", "A_B", "A\n"])
def test_code_rejects_invalid_value_with_exit_three(value):
    with pytest.raises(Rejected) as info:
        validate_code(value)
    assert info.value.exit_code == 3


def test_code_rejects_non_text():
    with pytest.raises(Rejected):
        validate_code(7)


@pytest.mark.parametrize("value", ["Front Drawer", "x", "x" * 40])
def test_name_accepts_valid_value_unchanged(value):
    assert validate_name(value) == value


@pytest.mark.parametrize("value", ["", "x" * 41, "a,b", "a\nb", "a\rb"])
def test_name_rejects_invalid_value_with_exit_three(value):
    with pytest.raises(Rejected) as info:
        validate_name(value)
    assert info.value.exit_code == 3


@pytest.mark.parametrize("value", ["", "walk in sale", "m" * 60])
def test_memo_accepts_valid_value_unchanged(value):
    assert validate_memo(value) == value


@pytest.mark.parametrize("value", ["m" * 61, "a,b", "a\nb", "a\rb"])
def test_memo_rejects_invalid_value_with_exit_three(value):
    with pytest.raises(Rejected) as info:
        validate_memo(value)
    assert info.value.exit_code == 3


@pytest.mark.parametrize("value", ["2026-04-01", "2024-02-29", "2026-12-31", "2000-02-29"])
def test_date_accepts_real_calendar_date_unchanged(value):
    assert validate_date(value) == value


@pytest.mark.parametrize(
    "value",
    ["2026-02-30", "2026-02-29", "2026-13-01", "2026-00-10", "2026-4-1", "20260401", "", "2026-04-01x", "1900-02-29", "0000-01-01"],
)
def test_date_rejects_impossible_or_malformed_value_with_exit_three(value):
    with pytest.raises(Rejected) as info:
        validate_date(value)
    assert info.value.exit_code == 3
