"""Amount validation: input parses to integer cents without floating point; output has exactly two decimals."""

import pytest

from cli.amount import format_amount, parse_amount


# parse_amount


@pytest.mark.parametrize(
    ("text", "cents"),
    [
        ("12.5", 1250),
        ("-0.05", -5),
        ("7", 700),
        ("0.1", 10),
        ("-3", -300),
        ("1.10", 110),
        ("0.01", 1),
        ("-0.01", -1),
        ("1.00", 100),
        ("007", 700),
        ("99999999999999", 9999999999999900),
    ],
)
def test_valid_amount_parses_to_signed_cents(text: str, cents: int) -> None:
    assert parse_amount(text) == cents


def test_parse_returns_int_never_float() -> None:
    assert type(parse_amount("1.10")) is int
    assert type(parse_amount("-7")) is int


@pytest.mark.parametrize(
    "text",
    [
        "0",
        "0.00",
        "-0",
        "-0.00",
        "0.0",
        "000",
    ],
)
def test_zero_amount_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(text)


@pytest.mark.parametrize("text", ["1.234", "0.001", "-0.999", "1.2345"])
def test_more_than_two_decimals_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(text)


@pytest.mark.parametrize(
    "text",
    [
        "1.",
        ".5",
        "1,00",
        "+5",
        "abc",
        "",
        " 1.00",
        "1.00 ",
        "1\n",
        "1.5.0",
        "--1",
        "-",
        "-.5",
        "1e3",
        "１.００",
    ],
)
def test_malformed_amount_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(text)


# format_amount


@pytest.mark.parametrize(
    ("cents", "text"),
    [
        (1250, "12.50"),
        (-5, "-0.05"),
        (10, "0.10"),
        (500000, "5000.00"),
        (-1250, "-12.50"),
        (1, "0.01"),
        (-1, "-0.01"),
        (0, "0.00"),
        (100, "1.00"),
        (123456789, "1234567.89"),
    ],
)
def test_cents_format_to_two_decimals(cents: int, text: str) -> None:
    assert format_amount(cents) == text


def test_format_has_no_thousands_separator() -> None:
    assert "," not in format_amount(123456789012)


# round trip


@pytest.mark.parametrize("text", ["12.50", "-0.05", "0.10", "5000.00", "-12.50"])
def test_canonical_text_round_trips_unchanged(text: str) -> None:
    assert format_amount(parse_amount(text)) == text
