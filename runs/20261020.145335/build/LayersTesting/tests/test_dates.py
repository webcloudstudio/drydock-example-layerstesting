"""Date validation: only real calendar dates written YYYY-MM-DD are accepted."""

import pytest

from cli.dates import check_date


@pytest.mark.parametrize(
    "text",
    [
        "2026-01-01",
        "2024-02-29",
        "2026-12-31",
        "2000-02-29",
        "2026-04-30",
        "0001-01-01",
        "9999-12-31",
    ],
)
def test_real_calendar_date_is_returned_unchanged(text: str) -> None:
    assert check_date(text) == text


@pytest.mark.parametrize(
    "text",
    [
        "2026-02-30",
        "2025-02-29",
        "1900-02-29",
        "2100-02-29",
        "2026-13-01",
        "2026-00-10",
        "2026-04-31",
        "2026-01-00",
        "0000-01-01",
    ],
)
def test_impossible_calendar_date_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        check_date(text)


@pytest.mark.parametrize(
    "text",
    [
        "2026-1-01",
        "2026-01-1",
        "26-01-01",
        "2026/01/01",
        "20260101",
        "01-01-2026",
        "2026-01-01 ",
        " 2026-01-01",
        "2026-01-01T00:00",
        "+026-01-01",
        "２０２６-01-01",
        "",
    ],
)
def test_malformed_shape_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        check_date(text)
