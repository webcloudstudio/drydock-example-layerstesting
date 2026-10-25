"""The non-negative balance rule across every mutating command: post, amend, delete, transfer, load.

Each test runs against a throwaway store in ``tmp_path``. It acts through ``cli_runner`` and reads
the outcome back through ``txn get``, ``account get``, or ``count``, never through diagnostic text.
"""

import csv
import io
from pathlib import Path

import pytest

from cli.testing import cli_runner

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    assert cli_runner("init")[0] == 0
    return tmp_path


def parse(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out, newline="")))


def write_csv(path: Path, header: list[str], rows: list[list]) -> str:
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return str(path)


def stored_txn_count() -> int:
    code, out, _ = cli_runner("count")
    assert code == 0
    return int(parse(out)[3][1])


def balance_of(account: str) -> str:
    code, out, _ = cli_runner("account", "get", account)
    assert code == 0
    return parse(out)[1][3]


def stored_txn(txn_id: int) -> list[str] | None:
    code, out, _ = cli_runner("txn", "get", str(txn_id))
    if code == 4:
        return None
    assert code == 0
    return parse(out)[1]


def make_account(code: str) -> None:
    assert cli_runner("account", "add", code, f"Name {code}")[0] == 0


def make_categories(tmp_path: Path, *codes: str) -> None:
    path = write_csv(tmp_path / "cats.csv", ["category", "description"],
                     [[code, f"Desc {code}"] for code in codes])
    assert cli_runner("load", "categories", path)[0] == 0


def post(account: str, category: str, amount: str, day: str = "2026-04-01"):
    return cli_runner("txn", "post", account, category, amount, day)


# txn post

def test_post_that_overdraws_is_rejected_and_writes_nothing(store, tmp_path):
    make_account("BRP")
    make_categories(tmp_path, "C")
    assert post("BRP", "C", "50.00")[0] == 0
    before = stored_txn_count()
    assert post("BRP", "C", "-50.01")[:2] == (3, "")
    assert stored_txn_count() == before
    assert balance_of("BRP") == "50.00"


def test_post_debit_against_an_empty_account_is_rejected(store, tmp_path):
    make_account("BRE")
    make_categories(tmp_path, "C")
    assert post("BRE", "C", "-0.01")[:2] == (3, "")
    assert stored_txn_count() == 0
    assert balance_of("BRE") == "0.00"


def test_post_that_brings_the_balance_to_exactly_zero_is_accepted(store, tmp_path):
    make_account("BRZ")
    make_categories(tmp_path, "C")
    assert post("BRZ", "C", "50.00")[0] == 0
    assert post("BRZ", "C", "-50.00")[0] == 0
    assert balance_of("BRZ") == "0.00"


# txn amend

def test_amend_that_overdraws_is_rejected_and_the_row_keeps_its_amount(store, tmp_path):
    make_account("BRA")
    make_categories(tmp_path, "C")
    assert post("BRA", "C", "50.00")[0] == 0
    assert post("BRA", "C", "-30.00")[0] == 0
    assert cli_runner("txn", "amend", "1", "29.99")[:2] == (3, "")
    assert stored_txn(1)[4] == "50.00"
    assert balance_of("BRA") == "20.00"


def test_amend_to_exactly_zero_is_accepted(store, tmp_path):
    make_account("BRAZ")
    make_categories(tmp_path, "C")
    assert post("BRAZ", "C", "50.00")[0] == 0
    assert post("BRAZ", "C", "-30.00")[0] == 0
    assert cli_runner("txn", "amend", "1", "30.00")[0] == 0
    assert balance_of("BRAZ") == "0.00"


def test_amend_that_raises_a_deposit_is_always_accepted(store, tmp_path):
    make_account("BRAR")
    make_categories(tmp_path, "C")
    assert post("BRAR", "C", "50.00")[0] == 0
    assert post("BRAR", "C", "-50.00")[0] == 0
    assert cli_runner("txn", "amend", "1", "80.00")[0] == 0
    assert balance_of("BRAR") == "30.00"


# txn delete

def test_delete_of_a_deposit_that_funds_a_later_debit_is_rejected_and_keeps_the_row(store, tmp_path):
    make_account("BRD")
    make_categories(tmp_path, "C")
    assert post("BRD", "C", "50.00")[0] == 0
    assert post("BRD", "C", "-50.00")[0] == 0
    before = stored_txn_count()
    assert cli_runner("txn", "delete", "1")[:2] == (3, "")
    assert stored_txn_count() == before
    assert stored_txn(1) is not None
    assert balance_of("BRD") == "0.00"


def test_delete_of_a_debit_is_accepted(store, tmp_path):
    make_account("BRDD")
    make_categories(tmp_path, "C")
    assert post("BRDD", "C", "50.00")[0] == 0
    assert post("BRDD", "C", "-50.00")[0] == 0
    assert cli_runner("txn", "delete", "2")[0] == 0
    assert balance_of("BRDD") == "50.00"


def test_delete_that_lands_exactly_on_zero_is_accepted(store, tmp_path):
    make_account("BRDZ")
    make_categories(tmp_path, "C")
    assert post("BRDZ", "C", "100.00")[0] == 0
    assert post("BRDZ", "C", "50.00")[0] == 0
    assert post("BRDZ", "C", "-50.00")[0] == 0
    # Removing the 100.00 deposit leaves 50.00 - 50.00 = 0.00, which is allowed.
    assert cli_runner("txn", "delete", "1")[0] == 0
    assert balance_of("BRDZ") == "0.00"


# transfer

def test_transfer_larger_than_the_source_is_rejected_and_writes_neither_row(store, tmp_path):
    make_account("BRTS")
    make_account("BRTD")
    make_categories(tmp_path, "C", "TRANSFER")
    assert post("BRTS", "C", "25.00")[0] == 0
    before = stored_txn_count()
    assert cli_runner("transfer", "BRTS", "BRTD", "25.01", "2026-04-03")[:2] == (3, "")
    assert stored_txn_count() == before
    assert balance_of("BRTS") == "25.00"
    assert balance_of("BRTD") == "0.00"


def test_transfer_from_an_empty_source_is_rejected(store, tmp_path):
    make_account("BRTE")
    make_account("BRTF")
    make_categories(tmp_path, "TRANSFER")
    assert cli_runner("transfer", "BRTE", "BRTF", "0.01", "2026-04-03")[:2] == (3, "")
    assert stored_txn_count() == 0


def test_transfer_of_exactly_the_source_balance_is_accepted(store, tmp_path):
    make_account("BRTX")
    make_account("BRTY")
    make_categories(tmp_path, "C", "TRANSFER")
    assert post("BRTX", "C", "25.00")[0] == 0
    assert cli_runner("transfer", "BRTX", "BRTY", "25.00", "2026-04-03")[0] == 0
    assert balance_of("BRTX") == "0.00"
    assert balance_of("BRTY") == "25.00"


# load transactions

def _load_setup(tmp_path: Path) -> None:
    make_account("BRLA")
    make_account("BRLB")
    make_categories(tmp_path, "C")


def _load(tmp_path: Path, rows: list[list], name: str = "rows.csv"):
    path = write_csv(tmp_path / name, TXN_HEADER, rows)
    return cli_runner("load", "transactions", path)


def test_load_whose_rows_overdraw_one_account_stores_none_of_them(store, tmp_path):
    _load_setup(tmp_path)
    assert _load(tmp_path, [
        [1, "2026-05-01", "BRLA", "C", "20.00", "deposit"],
        [2, "2026-05-01", "BRLB", "C", "10.00", "deposit"],
        [3, "2026-05-02", "BRLA", "C", "-20.01", "overdraw"],
    ])[:2] == (3, "")
    assert stored_txn_count() == 0
    assert stored_txn(1) is None
    assert stored_txn(2) is None


def test_load_debit_beyond_the_stored_balance_is_rejected(store, tmp_path):
    _load_setup(tmp_path)
    assert _load(tmp_path, [[1, "2026-05-01", "BRLA", "C", "10.00", "seed"]], "seed.csv")[0] == 0
    assert _load(tmp_path, [[2, "2026-05-02", "BRLA", "C", "-10.01", "debit"]], "debit.csv")[:2] == (3, "")
    assert balance_of("BRLA") == "10.00"
    assert stored_txn(2) is None


def test_load_whose_rows_net_to_exactly_zero_for_an_account_is_accepted(store, tmp_path):
    _load_setup(tmp_path)
    assert _load(tmp_path, [
        [1, "2026-05-01", "BRLA", "C", "15.00", "deposit"],
        [2, "2026-05-02", "BRLA", "C", "-15.00", "debit"],
    ])[0] == 0
    assert balance_of("BRLA") == "0.00"


# every mutating command, one rejection each

def _reject_post(tmp_path):
    make_account("RJP")
    make_categories(tmp_path, "C")
    return lambda: post("RJP", "C", "-1.00")


def _reject_amend(tmp_path):
    make_account("RJA")
    make_categories(tmp_path, "C")
    assert post("RJA", "C", "1.00")[0] == 0
    return lambda: cli_runner("txn", "amend", "1", "-1.00")


def _reject_delete(tmp_path):
    make_account("RJD")
    make_categories(tmp_path, "C")
    assert post("RJD", "C", "5.00")[0] == 0
    assert post("RJD", "C", "-5.00")[0] == 0
    return lambda: cli_runner("txn", "delete", "1")


def _reject_transfer(tmp_path):
    make_account("RJTS")
    make_account("RJTD")
    make_categories(tmp_path, "TRANSFER")
    return lambda: cli_runner("transfer", "RJTS", "RJTD", "1.00", "2026-04-03")


def _reject_load(tmp_path):
    make_account("RJLA")
    make_categories(tmp_path, "C")
    path = write_csv(tmp_path / "over.csv", TXN_HEADER,
                     [[1, "2026-05-01", "RJLA", "C", "-1.00", "overdraw"]])
    return lambda: cli_runner("load", "transactions", path)


@pytest.mark.parametrize("setup", [_reject_post, _reject_amend, _reject_delete,
                                   _reject_transfer, _reject_load],
                         ids=["post", "amend", "delete", "transfer", "load"])
def test_every_mutating_command_rejects_a_negative_balance_with_exit_three_and_no_stdout(
        store, tmp_path, setup):
    attempt = setup(tmp_path)
    before = stored_txn_count()
    code, out, _ = attempt()
    assert code == 3
    assert out == ""
    assert stored_txn_count() == before
