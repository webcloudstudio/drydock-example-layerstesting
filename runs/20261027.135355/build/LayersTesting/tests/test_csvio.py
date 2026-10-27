"""CSV reader: header checks, numbered rows, and the exception each failure raises."""

import csv
import os

import pytest

from ledger_core.csvio import read_rows
from ledger_core.errors import Operational, Rejected

HEADER = ["account", "name"]


def _write(path, text: str) -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(text)
    return str(path)


def test_returns_every_data_row_with_file_line_numbers(tmp_path):
    path = _write(tmp_path / "in.csv", "account,name\nZZR1,First\nZZR2,Second\nZZR3,Third\n")
    assert read_rows(path, HEADER) == [
        (2, ["ZZR1", "First"]),
        (3, ["ZZR2", "Second"]),
        (4, ["ZZR3", "Third"]),
    ]


def test_header_only_yields_no_rows(tmp_path):
    path = _write(tmp_path / "in.csv", "account,name\n")
    assert read_rows(path, HEADER) == []


def test_blank_lines_are_skipped_but_still_counted(tmp_path):
    path = _write(tmp_path / "in.csv", "account,name\n\nZZR1,First\n\nZZR2,Second\n")
    assert read_rows(path, HEADER) == [(3, ["ZZR1", "First"]), (5, ["ZZR2", "Second"])]


def test_quoted_field_with_comma_is_one_field(tmp_path):
    path = _write(tmp_path / "in.csv", 'account,name\nZZR1,"Quoted, Name"\n')
    assert read_rows(path, HEADER) == [(2, ["ZZR1", "Quoted, Name"])]


def test_fields_match_what_the_csv_module_parses(tmp_path):
    body = [["ZZR1", "Alpha"], ["ZZR2", "Beta gamma"]]
    path = tmp_path / "in.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(body)
    assert [fields for _, fields in read_rows(str(path), HEADER)] == body


def test_missing_file_is_operational(tmp_path):
    with pytest.raises(Operational):
        read_rows(str(tmp_path / "absent.csv"), HEADER)


def test_directory_is_operational(tmp_path):
    with pytest.raises(Operational):
        read_rows(str(tmp_path), HEADER)


def test_undecodable_file_is_operational(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"account,name\nZZR1,\xff\xfe\n")
    with pytest.raises(Operational):
        read_rows(str(path), HEADER)


@pytest.mark.parametrize(
    "header_line",
    ["name,account", "account", "account,name,extra", "code,name", "Account,name", " account,name"],
)
def test_wrong_header_is_rejected(tmp_path, header_line):
    path = _write(tmp_path / "in.csv", f"{header_line}\nZZR1,First\n")
    with pytest.raises(Rejected):
        read_rows(path, HEADER)


def test_empty_file_is_rejected(tmp_path):
    path = _write(tmp_path / "empty.csv", "")
    with pytest.raises(Rejected):
        read_rows(path, HEADER)


@pytest.mark.parametrize("body", ["ZZR1\n", "ZZR1,First,Extra\n"])
def test_wrong_field_count_is_rejected(tmp_path, body):
    path = _write(tmp_path / "rows.csv", "account,name\n" + body)
    with pytest.raises(Rejected):
        read_rows(path, HEADER)


def test_rejection_names_the_offending_line(tmp_path):
    path = _write(tmp_path / "rows.csv", "account,name\nZZR1,First\nZZR2\n")
    with pytest.raises(Rejected, match="line 3"):
        read_rows(path, HEADER)


def test_reader_never_writes_the_file(tmp_path):
    path = _write(tmp_path / "in.csv", "account,name\nZZR1,First\n")
    before = os.stat(path).st_mtime_ns
    with open(path, "rb") as fh:
        content = fh.read()
    read_rows(path, HEADER)
    with open(path, "rb") as fh:
        assert fh.read() == content
    assert os.stat(path).st_mtime_ns == before


def test_load_naming_missing_file_exits_one_and_stores_nothing(ledger_store, store_open, tmp_path):
    from cli.testing import cli_runner

    code, out, _ = cli_runner("load", "accounts", str(tmp_path / "missing.csv"))
    assert code == 1
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.accounts.list() == []


def test_load_naming_bad_header_exits_three(ledger_store, tmp_path):
    from cli.testing import cli_runner

    path = _write(tmp_path / "bad.csv", "code,name\nZZR1,First\n")
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
