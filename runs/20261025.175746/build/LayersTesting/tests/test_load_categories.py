"""``ledger load categories``: all-or-nothing validation of the whole file."""

from __future__ import annotations

import csv
import os

import pytest

from cli.testing import cli_runner


def _write(directory, name: str, rows: list[list[str]], header=("category", "description")) -> str:
    path = os.path.join(directory, name)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(list(header))
        writer.writerows(rows)
    return path


def test_valid_file_loads_every_row_and_reports_the_count(scratch_db, tmp_path):
    rows = [["UTKA1", "Cat One"], ["UTKA2", "Cat Two"]]
    code, out, _ = cli_runner("load", "categories", _write(tmp_path, "c.csv", rows))
    assert code == 0
    assert list(csv.reader(out.splitlines())) == [["table", "loaded"], ["categories", "2"]]
    for category, description in rows:
        stored = scratch_db.categories.get(category=category)
        assert stored is not None
        assert stored.description == description


def test_invalid_last_row_exits_3_and_stores_none_of_the_valid_rows(scratch_db, tmp_path):
    good = [["UTKB1", "Good One"], ["UTKB2", "Good Two"]]
    path = _write(tmp_path, "c.csv", good + [["UTK-B3", "Hyphen Code"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    for category, _ in good:
        assert scratch_db.categories.get(category=category) is None


@pytest.mark.parametrize(
    "variant",
    [["K" * 13, "Long Code"], ["UTKC1", ""], ["UTKC2", "D" * 41]],
    ids=["code-too-long", "empty-description", "description-too-long"],
)
def test_field_rule_violation_rejects_the_whole_file(scratch_db, tmp_path, variant):
    anchor = ["UTKC0", "Anchor"]
    code, out, _ = cli_runner("load", "categories", _write(tmp_path, "c.csv", [anchor, variant]))
    assert code == 3
    assert out == ""
    assert scratch_db.categories.get(category=anchor[0]) is None


def test_code_repeated_within_the_file_rejects_the_whole_file(scratch_db, tmp_path):
    path = _write(tmp_path, "within.csv", [["UTKD3", "First"], ["UTKD3", "Second"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert scratch_db.categories.get(category="UTKD3") is None


def test_code_already_stored_rejects_the_file_and_stores_nothing_new(scratch_db, tmp_path):
    scratch_db.categories.create(category="UTKD1", description="Already Here")
    path = _write(tmp_path, "store.csv", [["UTKD2", "Fresh"], ["UTKD1", "Clash"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert scratch_db.categories.get(category="UTKD2") is None
    assert scratch_db.categories.get(category="UTKD1").description == "Already Here"


def test_mismatched_header_exits_3_and_stores_nothing(scratch_db, tmp_path):
    path = _write(tmp_path, "wrong.csv", [["UTKE1", "Wrong Header"]], header=("account", "name"))
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert scratch_db.categories.get(category="UTKE1") is None


def test_missing_file_exits_1_with_no_stdout(scratch_db, tmp_path):
    code, out, _ = cli_runner("load", "categories", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""


def test_missing_file_argument_is_a_usage_error(scratch_db):
    code, out, _ = cli_runner("load", "categories")
    assert code == 2
    assert out == ""


def test_row_with_wrong_field_count_rejects_the_whole_file(scratch_db, tmp_path):
    path = tmp_path / "fields.csv"
    path.write_text("category,description\nUTKF1,Ok\nUTKF2\n", encoding="utf-8")
    code, out, _ = cli_runner("load", "categories", str(path))
    assert code == 3
    assert out == ""
    assert scratch_db.categories.get(category="UTKF1") is None


def test_boundary_code_and_description_lengths_are_accepted(scratch_db, tmp_path):
    rows = [["A" * 12, "D" * 40]]
    code, _, _ = cli_runner("load", "categories", _write(tmp_path, "edge.csv", rows))
    assert code == 0
    assert scratch_db.categories.get(category="A" * 12).description == "D" * 40


def test_empty_data_section_loads_zero_rows(scratch_db, tmp_path):
    code, out, _ = cli_runner("load", "categories", _write(tmp_path, "none.csv", []))
    assert code == 0
    assert out == "table,loaded\ncategories,0\n"
