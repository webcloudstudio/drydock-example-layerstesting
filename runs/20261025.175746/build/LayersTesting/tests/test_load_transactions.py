"""``ledger load transactions``: validation of the whole file before the first write."""

from __future__ import annotations

import csv
import os

import pytest

from cli.testing import cli_runner

HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


def _write(directory, name: str, rows: list[list], header=HEADER) -> str:
    path = os.path.join(directory, name)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(list(header))
        writer.writerows(rows)
    return path


@pytest.fixture
def ledger(scratch_db):
    scratch_db.accounts.create(account="LTA", name="Load Account")
    scratch_db.categories.create(category="LTC", description="Load Category")
    return scratch_db


def test_valid_file_keeps_file_txn_ids_and_stores_integer_cents(ledger, tmp_path):
    rows = [
        [910001, "2026-05-01", "LTA", "LTC", "100.00", "opening"],
        [910002, "2026-05-02", "LTA", "LTC", "-25.50", "spend"],
        [910007, "2026-05-03", "LTA", "LTC", "4.75", "gap id kept"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "t.csv", rows))
    assert code == 0
    assert list(csv.reader(out.splitlines())) == [["table", "loaded"], ["transactions", "3"]]
    stored = ledger.transactions.get(txn_id=910007)
    assert stored.amount == 475
    assert isinstance(stored.amount, int)
    assert stored.memo == "gap id kept"
    assert ledger.transactions.get(txn_id=910002).amount == -2550


def test_empty_data_section_loads_zero_rows(ledger, tmp_path):
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "e.csv", []))
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1] == ["transactions", "0"]


def test_unknown_account_in_last_row_stores_none_of_the_valid_rows(ledger, tmp_path):
    rows = [
        [920001, "2026-05-01", "LTA", "LTC", "10.00", "ok"],
        [920002, "2026-05-01", "LTNONE", "LTC", "10.00", "bad"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "a.csv", rows))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=920001) is None


def test_unknown_category_in_last_row_stores_none_of_the_valid_rows(ledger, tmp_path):
    rows = [
        [920011, "2026-05-01", "LTA", "LTC", "10.00", "ok"],
        [920012, "2026-05-01", "LTA", "LTNONE", "10.00", "bad"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "c.csv", rows))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=920011) is None


@pytest.mark.parametrize(
    "bad",
    [
        [920022, "2026-02-30", "LTA", "LTC", "1.00", "bad date"],
        [920023, "2026-05-01", "LTA", "LTC", "1.234", "three decimals"],
        [920024, "2026-05-01", "LTA", "LTC", "0.00", "zero"],
        ["abc", "2026-05-01", "LTA", "LTC", "1.00", "bad id"],
        [920025, "2026-05-01", "LTA", "LTC", "1.00", "N" * 61],
        [920026, "2026-05-01", "LTA", "LTC", "1.00", "has,comma"],
    ],
    ids=["impossible-date", "third-decimal", "zero-amount", "non-integer-id", "memo-too-long", "memo-comma"],
)
def test_field_rule_violation_rejects_the_whole_file(ledger, tmp_path, bad):
    anchor = [920021, "2026-05-01", "LTA", "LTC", "5.00", "anchor"]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "f.csv", [anchor, bad]))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=anchor[0]) is None


def test_id_repeated_within_the_file_is_refused(ledger, tmp_path):
    rows = [
        [930001, "2026-05-01", "LTA", "LTC", "1.00", "one"],
        [930001, "2026-05-01", "LTA", "LTC", "2.00", "two"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "d.csv", rows))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=930001) is None


def test_id_already_stored_is_refused_and_stored_row_is_unchanged(ledger, tmp_path):
    ledger.transactions.create(
        txn_id=930011, date="2026-05-01", account="LTA", category="LTC", amount=5000, memo="stored"
    )
    rows = [
        [930012, "2026-05-02", "LTA", "LTC", "1.00", "fresh"],
        [930011, "2026-05-02", "LTA", "LTC", "1.00", "clash"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "s.csv", rows))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=930012) is None
    assert ledger.transactions.get(txn_id=930011).amount == 5000


def test_final_balance_below_zero_refuses_the_whole_file(ledger, tmp_path):
    other = "LTB"
    ledger.accounts.create(account=other, name="Other")
    rows = [
        [940001, "2026-05-01", other, "LTC", "100.00", "fine"],
        [940002, "2026-05-01", "LTA", "LTC", "-0.01", "overdraw"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "o.csv", rows))
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=940001) is None
    assert ledger.transactions.get(txn_id=940002) is None


def test_balance_is_checked_on_the_final_total_after_the_whole_file(ledger, tmp_path):
    rows = [
        [940011, "2026-05-01", "LTA", "LTC", "-10.00", "spend first"],
        [940012, "2026-05-02", "LTA", "LTC", "10.00", "deposit later"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path, "g.csv", rows))
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1] == ["transactions", "2"]


def test_mismatched_header_exits_3_and_stores_nothing(ledger, tmp_path):
    path = _write(tmp_path, "w.csv", [[950001, "x"]], header=["account", "name"])
    code, out, _ = cli_runner("load", "transactions", path)
    assert code == 3
    assert out == ""
    assert ledger.transactions.get(txn_id=950001) is None


def test_missing_file_exits_1_with_no_stdout(ledger, tmp_path):
    code, out, _ = cli_runner("load", "transactions", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""


def test_missing_file_argument_is_a_usage_error(ledger):
    code, out, _ = cli_runner("load", "transactions")
    assert code == 2
    assert out == ""
