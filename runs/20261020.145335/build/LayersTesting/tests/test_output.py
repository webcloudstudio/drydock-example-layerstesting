"""CSV output and diagnostic rendering: header and rows as plain comma-separated lines."""

from cli.output import render_csv, render_diagnostic


def _split_lines(text: str) -> list[list[str]]:
    return [line.split(",") for line in text.split("\n")[:-1]]


def test_csv_writes_header_then_rows_in_order() -> None:
    header = ["account", "name"]
    rows = [["DRAWER1", "Front Drawer"], ["SAFE", "Store Safe"]]
    text = render_csv(header, rows)
    assert _split_lines(text) == [header] + rows


def test_csv_terminates_every_line_with_newline() -> None:
    rows = [["DRAWER1", "Front Drawer"], ["SAFE", "Store Safe"]]
    text = render_csv(["account", "name"], rows)
    assert text.count("\n") == len(rows) + 1
    assert text.endswith("\n")
    assert text.split("\n")[-1] == ""


def test_csv_with_no_rows_writes_only_header_line() -> None:
    header = ["table", "rows"]
    text = render_csv(header, [])
    assert _split_lines(text) == [header]
    assert text.count("\n") == 1


def test_csv_with_one_row_writes_header_and_that_row() -> None:
    text = render_csv(["table", "rows"], [["accounts", "4"]])
    assert _split_lines(text) == [["table", "rows"], ["accounts", "4"]]


def test_csv_with_many_rows_keeps_every_row_in_order() -> None:
    rows = [[str(i), f"item-{i}"] for i in range(250)]
    text = render_csv(["id", "label"], rows)
    assert _split_lines(text) == [["id", "label"]] + rows


def test_csv_with_empty_field_keeps_the_empty_field() -> None:
    text = render_csv(["account", "memo"], [["SAFE", ""]])
    assert _split_lines(text) == [["account", "memo"], ["SAFE", ""]]


def test_csv_adds_no_leading_or_trailing_spaces() -> None:
    text = render_csv(["table", "rows"], [["accounts", "4"], ["categories", "7"]])
    assert all(line == line.strip() for line in text.split("\n"))


def test_csv_does_not_alter_field_values() -> None:
    value = "  spaced \"quoted\" value  "
    text = render_csv(["memo"], [[value]])
    assert _split_lines(text)[1] == [value]


def test_csv_writes_no_quoting_around_fields() -> None:
    text = render_csv(["name"], [["Front Drawer"]])
    assert '"' not in text


def test_diagnostic_is_returned_as_exactly_one_line() -> None:
    message = "account DRAWER9 not found"
    text = render_diagnostic(message)
    assert text.rstrip("\n") == message
    assert text.count("\n") == 1


def test_diagnostic_appends_single_newline_to_message() -> None:
    assert render_diagnostic("insufficient funds") == "insufficient funds\n"


def test_diagnostic_of_empty_message_is_one_newline() -> None:
    assert render_diagnostic("") == "\n"


def test_diagnostic_does_not_alter_message_text() -> None:
    message = "  date must be written YYYY-MM-DD: '2026-1-01'  "
    assert render_diagnostic(message) == message + "\n"
