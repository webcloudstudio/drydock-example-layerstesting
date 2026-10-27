"""Amount text to integer cents, and integer cents to two-decimal text."""

import pytest

from ledger_core.errors import Rejected
from ledger_core.money import format_cents, parse_amount


@pytest.mark.parametrize(
    ("text", "cents"),
    [("45.50", 4550), ("-12.34", -1234), ("7", 700), ("1.5", 150), ("0.01", 1),
     ("5000.00", 500000), ("-0.99", -99), ("-3", -300)],
)
def test_parse_returns_integer_cents(text, cents):
    value = parse_amount(text)
    assert type(value) is int
    assert value == cents


@pytest.mark.parametrize(
    "text",
    ["0", "0.00", "-0", "-0.0", "1.234", "1.000", "abc", "1.", ".5", "+5", "1,5", "", "-", "1 .5", "--5", " 5", "5 "],
)
def test_parse_rejects_invalid_text_with_exit_three(text):
    with pytest.raises(Rejected) as info:
        parse_amount(text)
    assert info.value.exit_code == 3


def test_parse_rejects_non_text():
    with pytest.raises(Rejected):
        parse_amount(5)


@pytest.mark.parametrize(
    ("cents", "text"),
    [(-1250, "-12.50"), (0, "0.00"), (500000, "5000.00"), (5, "0.05"), (-5, "-0.05"), (123456789, "1234567.89")],
)
def test_format_writes_two_decimals_without_separator(cents, text):
    assert format_cents(cents) == text


@pytest.mark.parametrize("cents", [1, -1, 99, 100, -100, 12345, -987654, 500000])
def test_parse_of_formatted_cents_round_trips(cents):
    assert parse_amount(format_cents(cents)) == cents


def test_format_rejects_non_integer_cents():
    with pytest.raises(Rejected):
        format_cents("12.50")
    with pytest.raises(Rejected):
        format_cents(True)
