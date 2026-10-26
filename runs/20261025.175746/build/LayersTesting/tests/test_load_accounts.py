"""``ledger load accounts``: all-or-nothing validation of the whole file."""

from __future__ import annotations

import csv
import os

import pytest

from cli.testing import cli_runner


def _write(directory, name: str, rows: list[list[str]], header=("account", "name")) -> str:
    path = os.path.join(directory, name)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(list(header))
        writer.writerows(rows)
    return path


def test_valid_file_loads_every_row_and_reports_the_count(scratch_db, tmp_path):
    rows = [["UTLA1", "Load One"], ["UTLA2", "Load Two"], ["UTLA3", "Load Three"]]
    code, out, _ = cli_runner("load", "accounts", _write(tmp_path, "a.csv", rows))
    assert code == 0
    assert list(csv.reader(out.splitlines())) == [["table", "loaded"], ["accounts", "3"]]
    for account, name in rows:
        stored = scratch_db.accounts.get(account=account)
        assert stored is not None
        assert stored.name == name


def test_invalid_last_row_exits_3_and_stores_none_of_the_valid_rows(scratch_db, tmp_path):
    good = [["UTLB1", "Good One"], ["UTLB2", "Good Two"]]
    path = _write(tmp_path, "a.csv", good + [["utlb3", "Lowercase Code"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    for account, _ in good:
        assert scratch_db.accounts.get(account=account) is None
    assert scratch_db.accounts.get(account="utlb3") is None


@pytest.mark.parametrize(
    "variant",
    [["A" * 13, "Long Code"], ["UTLC1", ""], ["UTLC2", "N" * 41]],
    ids=["code-too-long", "empty-name", "name-too-long"],
)
def test_field_rule_violation_rejects_the_whole_file(scratch_db, tmp_path, variant):
    anchor = ["UTLC0", "Anchor"]
    code, out, _ = cli_runner("load", "accounts", _write(tmp_path, "a.csv", [anchor, variant]))
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account=anchor[0]) is None


def test_code_repeated_within_the_file_rejects_the_whole_file(scratch_db, tmp_path):
    path = _write(tmp_path, "within.csv", [["UTLD3", "First"], ["UTLD3", "Second"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="UTLD3") is None


def test_code_already_stored_rejects_the_file_and_leaves_the_stored_row(scratch_db, tmp_path):
    scratch_db.accounts.create(account="UTLD1", name="Already Here")
    path = _write(tmp_path, "store.csv", [["UTLD2", "Fresh"], ["UTLD1", "Clash"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="UTLD2") is None
    assert scratch_db.accounts.get(account="UTLD1").name == "Already Here"


def test_mismatched_header_exits_3_and_stores_nothing(scratch_db, tmp_path):
    path = _write(tmp_path, "wrong.csv", [["Swapped", "UTLE1"]], header=("name", "account"))
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="UTLE1") is None


def test_missing_file_exits_1_with_no_stdout(scratch_db, tmp_path):
    code, out, _ = cli_runner("load", "accounts", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""


def test_missing_file_argument_is_a_usage_error(scratch_db):
    code, out, _ = cli_runner("load", "accounts")
    assert code == 2
    assert out == ""


def test_extra_file_argument_is_a_usage_error(scratch_db, tmp_path):
    path = _write(tmp_path, "a.csv", [["UTLF1", "Extra"]])
    code, out, _ = cli_runner("load", "accounts", path, path)
    assert code == 2
    assert out == ""
    assert scratch_db.accounts.get(account="UTLF1") is None


def test_unknown_table_is_a_usage_error(scratch_db, tmp_path):
    path = _write(tmp_path, "a.csv", [["UTLG1", "Unknown Table"]])
    code, out, _ = cli_runner("load", "nosuchtable", path)
    assert code == 2
    assert out == ""


def test_row_with_wrong_field_count_rejects_the_whole_file(scratch_db, tmp_path):
    path = tmp_path / "fields.csv"
    path.write_text("account,name\nUTLH1,Ok\nUTLH2,Too,Many\n", encoding="utf-8")
    code, out, _ = cli_runner("load", "accounts", str(path))
    assert code == 3
    assert out == ""
    assert scratch_db.accounts.get(account="UTLH1") is None


def test_boundary_code_and_name_lengths_are_accepted(scratch_db, tmp_path):
    code, _, _ = cli_runner("load", "accounts", _write(tmp_path, "edge.csv", [["Z" * 12, "N" * 40]]))
    assert code == 0
    assert scratch_db.accounts.get(account="Z" * 12).name == "N" * 40
