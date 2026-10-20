"""Text validation: codes, names, descriptions, and memos are checked before any write."""

import pytest

from cli.text_validation import check_code, check_memo, check_name


# check_code


@pytest.mark.parametrize("text", ["A", "AB12", "Z9", "0", "A" * 12, "1" * 12])
def test_valid_code_is_returned_unchanged(text: str) -> None:
    assert check_code(text) == text


@pytest.mark.parametrize(
    "text",
    [
        "",
        "ab",
        "a",
        "A-1",
        "A B",
        "A_1",
        "A" * 13,
        "A\n",
        " A",
        "Ä",
    ],
)
def test_invalid_code_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        check_code(text)


# check_name


@pytest.mark.parametrize("text", ["N", "Front Drawer", "N" * 40, "Café Ünïcode"])
def test_valid_name_is_returned_unchanged(text: str) -> None:
    assert check_name(text) == text


@pytest.mark.parametrize("text", ["", "N" * 41, "a,b", "a\nb", "a\rb", ",", "\n"])
def test_invalid_name_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        check_name(text)


def test_name_is_not_normalized() -> None:
    assert check_name("  padded  ") == "  padded  "


# check_memo


@pytest.mark.parametrize("text", ["", "walk in sale", "m" * 60, " "])
def test_valid_memo_is_returned_unchanged(text: str) -> None:
    assert check_memo(text) == text


@pytest.mark.parametrize("text", ["m" * 61, "a,b", "a\nb", "a\rb", ","])
def test_invalid_memo_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        check_memo(text)


def test_empty_memo_is_accepted_but_empty_name_is_not() -> None:
    assert check_memo("") == ""
    with pytest.raises(ValueError):
        check_name("")
