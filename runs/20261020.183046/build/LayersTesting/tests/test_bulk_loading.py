from __future__ import annotations

import csv
from pathlib import Path

from cli.testing import cli_runner


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def run_in_store(monkeypatch, tmp_path: Path, args: tuple[str, ...]) -> tuple[int, str, str]:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    return cli_runner(*args)


def test_valid_account_file_reports_count_and_round_trips_rows(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "accounts.csv"
    write_csv(path, [["account", "name"], ["A1", "Main"], ["A2", "Reserve"]])
    assert run_in_store(monkeypatch, tmp_path, ("init",))[0] == 0
    code, output, error = run_in_store(monkeypatch, tmp_path, ("load", "accounts", str(path)))
    assert code == 0
    assert error == ""
    assert list(csv.reader(output.splitlines()))[-1] == ["accounts", "2"]
    code, output, _ = run_in_store(monkeypatch, tmp_path, ("count",))
    assert code == 0
    assert list(csv.reader(output.splitlines()))[1] == ["accounts", "2"]


def test_invalid_account_row_is_atomic(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "accounts.csv"
    write_csv(path, [["account", "name"], ["A1", "Main"], ["bad-code!", "Invalid"]])
    assert run_in_store(monkeypatch, tmp_path, ("init",))[0] == 0
    code, output, _ = run_in_store(monkeypatch, tmp_path, ("load", "accounts", str(path)))
    assert code == 3
    assert output == ""
    code, output, _ = run_in_store(monkeypatch, tmp_path, ("count",))
    assert code == 0
    assert list(csv.reader(output.splitlines()))[1] == ["accounts", "0"]


def test_transaction_unknown_reference_is_atomic(monkeypatch, tmp_path: Path) -> None:
    account_path = tmp_path / "accounts.csv"
    transaction_path = tmp_path / "transactions.csv"
    write_csv(account_path, [["account", "name"], ["A1", "Main"]])
    write_csv(transaction_path, [["txn_id", "date", "account", "category", "amount", "memo"],
                                 ["1", "2026-01-01", "NOSUCH", "SALES", "1.00", "bad"]])
    assert run_in_store(monkeypatch, tmp_path, ("init",))[0] == 0
    assert run_in_store(monkeypatch, tmp_path, ("load", "accounts", str(account_path)))[0] == 0
    code, output, _ = run_in_store(monkeypatch, tmp_path, ("load", "transactions", str(transaction_path)))
    assert code == 3
    assert output == ""
    code, output, _ = run_in_store(monkeypatch, tmp_path, ("count",))
    assert code == 0
    assert list(csv.reader(output.splitlines()))[3] == ["transactions", "0"]


def test_amount_date_header_and_balance_are_rejected_before_writes(monkeypatch, tmp_path: Path) -> None:
    account_path = tmp_path / "accounts.csv"
    write_csv(account_path, [["account", "name"], ["A1", "Main"]])
    assert run_in_store(monkeypatch, tmp_path, ("init",))[0] == 0
    assert run_in_store(monkeypatch, tmp_path, ("load", "accounts", str(account_path)))[0] == 0
    for txn_id, name, amount, txn_date in ((1, "bad_amount", "1.234", "2026-01-01"),
                                            (2, "bad_date", "1.00", "2026-02-30"),
                                            (3, "negative", "-1.00", "2026-01-01")):
        path = tmp_path / f"{name}.csv"
        write_csv(path, [["txn_id", "date", "account", "category", "amount", "memo"],
                         [str(txn_id), txn_date, "A1", "SALES", amount, "memo"]])
        assert run_in_store(monkeypatch, tmp_path, ("load", "transactions", str(path)))[0] == 3
    assert run_in_store(monkeypatch, tmp_path, ("count",))[0] == 0

