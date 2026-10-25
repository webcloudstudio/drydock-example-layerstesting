"""Behavior of the ledger commands, each run against a throwaway store in ``tmp_path``.

Every test acts through ``cli_runner`` and reads the outcome back through a command or the stored
row, never through captured diagnostic text. Seed files are read only to load them, and no test
touches the application store.
"""

import csv
import io
from pathlib import Path

import pytest

from cli.testing import cli_runner

SOURCES = Path(__file__).resolve().parent.parent / "sources"
ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]
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


def table_counts() -> list[int]:
    code, out, _ = cli_runner("count")
    assert code == 0
    return [int(row[1]) for row in parse(out)[1:]]


def make_account(code: str, name: str | None = None) -> None:
    assert cli_runner("account", "add", code, name or f"Name {code}")[0] == 0


def make_categories(tmp_path: Path, *codes: str) -> None:
    path = write_csv(tmp_path / "cats.csv", ["category", "description"],
                     [[code, f"Desc {code}"] for code in codes])
    assert cli_runner("load", "categories", path)[0] == 0


def post(account: str, category: str, amount: str, day: str = "2026-04-01", memo: str = ""):
    args = ["txn", "post", account, category, amount, day]
    if memo:
        args.append(memo)
    return cli_runner(*args)


def balance_of(account: str) -> str:
    code, out, _ = cli_runner("account", "get", account)
    assert code == 0
    return parse(out)[1][3]


def stored_count() -> int:
    return table_counts()[2]


# init and count

def test_init_on_a_brand_new_store_creates_the_tables(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "fresh" / "ledger.db"))
    code, out, _ = cli_runner("init")
    assert (code, out) == (0, "")
    assert table_counts() == [0, 0, 0]


def test_init_prints_nothing_and_is_repeatable(store):
    assert cli_runner("init") == (0, "", "")
    assert cli_runner("init") == (0, "", "")


def test_init_empties_all_three_tables(store):
    make_account("INITA")
    make_categories(store, "INITC")
    assert post("INITA", "INITC", "5.00")[0] == 0
    assert table_counts() == [1, 1, 1]
    assert cli_runner("init")[0] == 0
    assert table_counts() == [0, 0, 0]


def test_init_with_an_extra_argument_is_usage_error_and_removes_nothing(store):
    make_account("INITK")
    code, out, _ = cli_runner("init", "extra")
    assert (code, out) == (2, "")
    assert table_counts() == [1, 0, 0]


def test_count_reports_each_table_in_order(store):
    make_account("CNTA")
    make_account("CNTB")
    assert cli_runner("count")[1] == "table,rows\naccounts,2\ncategories,0\ntransactions,0\n"


def test_count_with_an_extra_argument_is_usage_error(store):
    code, out, err = cli_runner("count", "extra")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1


# account add, get, rename, delete

def test_account_add_prints_the_zero_balance_row(store):
    code, out, _ = cli_runner("account", "add", "ADDOK1", "Added Account")
    assert code == 0
    assert parse(out) == [ACCOUNT_HEADER, ["ADDOK1", "Added Account", "0", "0.00"]]
    assert parse(cli_runner("account", "get", "ADDOK1")[1]) == parse(out)


def test_account_add_accepts_a_twelve_character_code_and_forty_character_name(store):
    code, out, _ = cli_runner("account", "add", "A" * 12, "N" * 40)
    assert code == 0
    assert parse(out)[1][:2] == ["A" * 12, "N" * 40]


@pytest.mark.parametrize("bad", ["ADDBADCODE123X", "addlower", "ADD-DASH", "ADD SPACE", ""])
def test_account_add_rejects_an_invalid_code_and_stores_nothing(store, bad):
    code, out, _ = cli_runner("account", "add", bad, "Some Name")
    assert (code, out) == (3, "")
    assert cli_runner("account", "get", bad)[0] == 4
    assert table_counts()[0] == 0


@pytest.mark.parametrize("bad", ["", "N" * 41, "has,comma", "has\nnewline"])
def test_account_add_rejects_an_invalid_name_and_stores_nothing(store, bad):
    code, out, _ = cli_runner("account", "add", "ADDBN", bad)
    assert (code, out) == (3, "")
    assert table_counts()[0] == 0


@pytest.mark.parametrize("args", [("account", "add"), ("account", "add", "A1"),
                                  ("account", "add", "A1", "Name", "extra")])
def test_account_add_wrong_argument_count_is_usage_error(store, args):
    code, out, _ = cli_runner(*args)
    assert (code, out) == (2, "")
    assert table_counts()[0] == 0


def test_duplicate_account_code_is_rejected_and_keeps_the_original(store):
    make_account("DUPA", "Original")
    code, out, _ = cli_runner("account", "add", "DUPA", "Different")
    assert (code, out) == (3, "")
    assert parse(cli_runner("account", "get", "DUPA")[1])[1][1] == "Original"
    assert table_counts()[0] == 1


def test_duplicate_account_code_with_the_same_name_is_still_rejected(store):
    make_account("DUPS", "Same")
    assert cli_runner("account", "add", "DUPS", "Same")[0] == 3


def test_a_different_code_succeeds_after_a_duplicate_rejection(store):
    make_account("DUPX", "First")
    assert cli_runner("account", "add", "DUPX", "Again")[0] == 3
    assert cli_runner("account", "add", "DUPY", "Second")[0] == 0
    assert table_counts()[0] == 2


def test_account_get_absent_is_not_found_with_empty_stdout(store):
    code, out, _ = cli_runner("account", "get", "NOPE")
    assert (code, out) == (4, "")


@pytest.mark.parametrize("args", [("account", "get"), ("account", "get", "ONE", "TWO")])
def test_account_get_wrong_argument_count_is_usage_error(store, args):
    assert cli_runner(*args)[:2] == (2, "")


def test_account_get_reports_count_and_balance_from_stored_cents(store, tmp_path):
    make_account("GETB")
    make_categories(tmp_path, "GETBC")
    assert post("GETB", "GETBC", "50.00")[0] == 0
    assert post("GETB", "GETBC", "-12.34")[0] == 0
    code, out, _ = cli_runner("account", "get", "GETB")
    assert parse(out) == [ACCOUNT_HEADER, ["GETB", "Name GETB", "2", "37.66"]]


def test_account_rename_changes_only_the_name_and_keeps_transactions(store, tmp_path):
    make_account("RENB", "Before")
    make_categories(tmp_path, "RENBC")
    assert post("RENB", "RENBC", "7.77", memo="keep")[0] == 0
    code, out, _ = cli_runner("account", "rename", "RENB", "After")
    assert code == 0
    assert parse(out) == [ACCOUNT_HEADER, ["RENB", "After", "1", "7.77"]]
    assert cli_runner("txn", "get", "1")[1].splitlines()[1] == "1,2026-04-01,RENB,RENBC,7.77,keep"


def test_account_rename_with_an_invalid_name_changes_nothing(store):
    make_account("RENI", "Original")
    for bad in ("N" * 41, "", "has,comma"):
        assert cli_runner("account", "rename", "RENI", bad)[:2] == (3, "")
    assert parse(cli_runner("account", "get", "RENI")[1])[1][1] == "Original"


def test_account_rename_absent_is_not_found_and_creates_nothing(store):
    assert cli_runner("account", "rename", "NOPE", "Whatever")[:2] == (4, "")
    assert table_counts()[0] == 0


@pytest.mark.parametrize("args", [("account", "rename"), ("account", "rename", "ONLY"),
                                  ("account", "rename", "A", "B", "C")])
def test_account_rename_wrong_argument_count_is_usage_error(store, args):
    assert cli_runner(*args)[:2] == (2, "")


def test_account_delete_removes_an_account_with_no_transactions(store):
    make_account("DELA")
    code, out, _ = cli_runner("account", "delete", "DELA")
    assert code == 0
    assert parse(out) == [["deleted"], ["DELA"]]
    assert cli_runner("account", "get", "DELA")[0] == 4


def test_account_delete_refuses_an_account_that_has_transactions(store, tmp_path):
    make_account("DELU")
    make_categories(tmp_path, "DELUC")
    assert post("DELU", "DELUC", "5.00")[0] == 0
    assert cli_runner("account", "delete", "DELU")[:2] == (3, "")
    assert cli_runner("account", "get", "DELU")[0] == 0
    assert table_counts() == [1, 1, 1]


def test_account_delete_absent_is_not_found(store):
    assert cli_runner("account", "delete", "NOPE")[:2] == (4, "")


def test_account_delete_leaves_other_accounts_in_place(store):
    make_account("KEEP1", "Kept")
    make_account("GONE1", "Gone")
    assert cli_runner("account", "delete", "GONE1")[0] == 0
    assert parse(cli_runner("account", "get", "KEEP1")[1])[1][1] == "Kept"
    assert table_counts()[0] == 1


@pytest.mark.parametrize("args", [("account", "delete"), ("account", "delete", "A", "B")])
def test_account_delete_wrong_argument_count_is_usage_error(store, args):
    assert cli_runner(*args)[:2] == (2, "")


# load categories and accounts

def test_load_categories_stores_every_row_and_reports_the_count(store, tmp_path):
    path = write_csv(tmp_path / "c.csv", ["category", "description"],
                     [["LDC1", "One"], ["LDC2", "Two"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 0
    assert parse(out) == [["table", "loaded"], ["categories", "2"]]
    assert table_counts()[1] == 2
    assert cli_runner("report", "categories")[1].splitlines()[1].startswith("LDC1,One,0,")


def test_load_categories_rejects_a_swapped_header_and_stores_nothing(store, tmp_path):
    path = write_csv(tmp_path / "c.csv", ["description", "category"], [["Swapped", "LDCH"]])
    assert cli_runner("load", "categories", path)[:2] == (3, "")
    assert table_counts()[1] == 0


def test_load_categories_is_all_or_nothing(store, tmp_path):
    path = write_csv(tmp_path / "c.csv", ["category", "description"],
                     [["LDCG", "Good row"], ["X" * 13, "Code too long"]])
    assert cli_runner("load", "categories", path)[:2] == (3, "")
    assert table_counts()[1] == 0


def test_load_categories_rejects_a_repeat_within_the_file_or_already_stored(store, tmp_path):
    twice = write_csv(tmp_path / "t.csv", ["category", "description"],
                      [["LDCD", "One"], ["LDCD", "Two"]])
    assert cli_runner("load", "categories", twice)[:2] == (3, "")
    once = write_csv(tmp_path / "o.csv", ["category", "description"], [["LDCE", "Only"]])
    assert cli_runner("load", "categories", once)[0] == 0
    assert cli_runner("load", "categories", once)[:2] == (3, "")
    assert table_counts()[1] == 1


def test_load_accounts_stores_every_row(store, tmp_path):
    path = write_csv(tmp_path / "a.csv", ["account", "name"], [["LDA1", "Name 1"], ["LDA2", "Name 2"]])
    assert cli_runner("load", "accounts", path) == (0, "table,loaded\naccounts,2\n", "")
    assert parse(cli_runner("account", "get", "LDA2")[1])[1][1] == "Name 2"


def test_load_accounts_rejects_a_wrong_header(store, tmp_path):
    path = write_csv(tmp_path / "a.csv", ["code", "label"], [["LDAH", "Wrong"]])
    assert cli_runner("load", "accounts", path)[:2] == (3, "")
    assert table_counts()[0] == 0


def test_load_accounts_rejects_an_invalid_row_and_stores_none(store, tmp_path):
    path = write_csv(tmp_path / "a.csv", ["account", "name"],
                     [["LDAG", "Good"], ["bad code", "Bad"]])
    assert cli_runner("load", "accounts", path)[:2] == (3, "")
    assert table_counts()[0] == 0


def test_load_accounts_rejects_a_repeat_in_the_file_or_already_stored(store, tmp_path):
    twice = write_csv(tmp_path / "t.csv", ["account", "name"], [["LDAD", "One"], ["LDAD", "Two"]])
    assert cli_runner("load", "accounts", twice)[:2] == (3, "")
    once = write_csv(tmp_path / "o.csv", ["account", "name"], [["LDAE", "Only"]])
    assert cli_runner("load", "accounts", once)[0] == 0
    assert cli_runner("load", "accounts", once)[:2] == (3, "")


@pytest.mark.parametrize("table", ["accounts", "categories", "transactions"])
def test_load_missing_argument_is_usage_error(store, table):
    assert cli_runner("load", table)[:2] == (2, "")


@pytest.mark.parametrize("table", ["accounts", "categories", "transactions"])
def test_load_unreadable_file_is_operational_failure(store, tmp_path, table):
    code, out, _ = cli_runner("load", table, str(tmp_path / "absent.csv"))
    assert (code, out) == (1, "")


# load transactions

def _txn_file(tmp_path: Path, rows: list[list], name: str = "t.csv") -> str:
    return write_csv(tmp_path / name, TXN_HEADER, rows)


def _referenced(tmp_path: Path) -> None:
    make_account("LTA1")
    make_account("LTA2")
    make_categories(tmp_path, "LTC1")


def test_load_transactions_keeps_file_ids_and_reads_back(store, tmp_path):
    _referenced(tmp_path)
    path = _txn_file(tmp_path, [
        [1001, "2026-05-01", "LTA1", "LTC1", "100.00", "deposit"],
        [1002, "2026-05-02", "LTA1", "LTC1", "-25.50", "payment"],
        [1003, "2026-05-03", "LTA1", "LTC1", "10.25", ""],
    ])
    assert cli_runner("load", "transactions", path) == (0, "table,loaded\ntransactions,3\n", "")
    assert parse(cli_runner("txn", "get", "1002")[1])[1] == ["1002", "2026-05-02", "LTA1", "LTC1", "-25.50", "payment"]
    assert parse(cli_runner("txn", "get", "1003")[1])[1][4:] == ["10.25", ""]
    assert balance_of("LTA1") == "84.75"


@pytest.mark.parametrize("bad_account, bad_category", [("LTNONE", "LTC1"), ("LTA1", "LTNONE")])
def test_load_transactions_rejects_an_unknown_reference(store, tmp_path, bad_account, bad_category):
    _referenced(tmp_path)
    path = _txn_file(tmp_path, [
        [1, "2026-05-01", "LTA1", "LTC1", "50.00", "ok"],
        [2, "2026-05-01", bad_account, bad_category, "5.00", "bad"],
    ])
    assert cli_runner("load", "transactions", path)[:2] == (3, "")
    assert table_counts()[2] == 0


@pytest.mark.parametrize("day, amount, memo", [
    ("2026-05-01", "1.234", "three decimals"),
    ("2026-05-01", "0.00", "zero"),
    ("2026-02-30", "5.00", "impossible date"),
    ("2026-05-01", "5.00", "m" * 61),
])
def test_load_transactions_rejects_an_invalid_field_and_stores_none(store, tmp_path, day, amount, memo):
    _referenced(tmp_path)
    path = _txn_file(tmp_path, [
        [1, "2026-05-01", "LTA1", "LTC1", "5.00", "fine"],
        [2, day, "LTA1", "LTC1", amount, memo],
    ])
    assert cli_runner("load", "transactions", path)[:2] == (3, "")
    assert table_counts()[2] == 0


@pytest.mark.parametrize("bad_id", ["abc", "0", "-4", "2147483648", "1.5"])
def test_load_transactions_rejects_a_non_positive_or_non_integer_id(store, tmp_path, bad_id):
    _referenced(tmp_path)
    path = _txn_file(tmp_path, [[bad_id, "2026-05-01", "LTA1", "LTC1", "5.00", ""]])
    assert cli_runner("load", "transactions", path)[:2] == (3, "")
    assert table_counts()[2] == 0


def test_load_transactions_rejects_a_repeat_in_the_file_or_already_stored(store, tmp_path):
    _referenced(tmp_path)
    twice = _txn_file(tmp_path, [
        [7, "2026-05-01", "LTA1", "LTC1", "10.00", "a"],
        [7, "2026-05-02", "LTA1", "LTC1", "10.00", "b"],
    ], "twice.csv")
    assert cli_runner("load", "transactions", twice)[:2] == (3, "")
    once = _txn_file(tmp_path, [[8, "2026-05-03", "LTA1", "LTC1", "10.00", "c"]], "once.csv")
    assert cli_runner("load", "transactions", once)[0] == 0
    assert cli_runner("load", "transactions", once)[:2] == (3, "")
    assert table_counts()[2] == 1


def test_load_transactions_rejects_a_file_that_overdraws_an_account(store, tmp_path):
    _referenced(tmp_path)
    path = _txn_file(tmp_path, [
        [1, "2026-05-01", "LTA2", "LTC1", "20.00", "deposit"],
        [2, "2026-05-02", "LTA2", "LTC1", "-20.01", "overdraw"],
    ])
    assert cli_runner("load", "transactions", path)[:2] == (3, "")
    assert table_counts()[2] == 0


# txn post, get, delete, amend

def test_txn_post_prints_the_row_with_the_next_id(store, tmp_path):
    make_account("TPA")
    make_categories(tmp_path, "TPC")
    code, out, _ = post("TPA", "TPC", "45.50", "2026-04-01", "walk in sale")
    assert code == 0
    assert parse(out) == [TXN_HEADER, ["1", "2026-04-01", "TPA", "TPC", "45.50", "walk in sale"]]


def test_txn_post_assigns_consecutive_ids(store, tmp_path):
    make_account("TPI")
    make_categories(tmp_path, "TPIC")
    assert parse(post("TPI", "TPIC", "10.00")[1])[1][0] == "1"
    assert parse(post("TPI", "TPIC", "20.00")[1])[1][0] == "2"


def test_txn_post_without_a_memo_stores_an_empty_memo(store, tmp_path):
    make_account("TPN")
    make_categories(tmp_path, "TPNC")
    assert parse(post("TPN", "TPNC", "3.00")[1])[1][5] == ""


def test_txn_post_accepts_a_negative_amount_with_funds_and_stores_it_as_negative_cents(store, tmp_path):
    make_account("TPG")
    make_categories(tmp_path, "TPGC")
    assert post("TPG", "TPGC", "50.00")[0] == 0
    code, out, _ = post("TPG", "TPGC", "-12.34", "2026-04-02", "tape")
    assert code == 0
    assert parse(out)[1][4] == "-12.34"
    assert balance_of("TPG") == "37.66"


def test_txn_post_that_would_overdraw_is_rejected_and_stores_nothing(store, tmp_path):
    make_account("TPO")
    make_categories(tmp_path, "TPOC")
    assert post("TPO", "TPOC", "10.00")[0] == 0
    assert post("TPO", "TPOC", "-10.01")[:2] == (3, "")
    assert table_counts()[2] == 1


def test_txn_post_that_leaves_exactly_zero_is_accepted(store, tmp_path):
    make_account("TPZ")
    make_categories(tmp_path, "TPZC")
    assert post("TPZ", "TPZC", "10.00")[0] == 0
    assert post("TPZ", "TPZC", "-10.00")[0] == 0
    assert balance_of("TPZ") == "0.00"


def test_txn_post_to_an_unknown_account_or_category_is_rejected(store, tmp_path):
    make_account("TPU")
    make_categories(tmp_path, "TPUC")
    assert post("NOPE", "TPUC", "1.00")[:2] == (3, "")
    assert post("TPU", "NOPE", "1.00")[:2] == (3, "")
    assert table_counts()[2] == 0


@pytest.mark.parametrize("amount", ["0", "0.0", "0.00", "-0.00", "1.234", "12.", "+5.00", "--1", "abc", ""])
def test_txn_post_rejects_a_malformed_or_zero_amount(store, tmp_path, amount):
    make_account("TPM")
    make_categories(tmp_path, "TPMC")
    assert post("TPM", "TPMC", amount)[:2] == (3, "")
    assert table_counts()[2] == 0


@pytest.mark.parametrize("day", ["2026-02-30", "2026-02-29", "2026-13-01", "2026-2-3", "notadate"])
def test_txn_post_rejects_an_impossible_or_malformed_date(store, tmp_path, day):
    make_account("TPD")
    make_categories(tmp_path, "TPDC")
    assert post("TPD", "TPDC", "1.00", day)[:2] == (3, "")
    assert table_counts()[2] == 0


def test_txn_post_accepts_a_leap_day_and_a_one_decimal_amount(store, tmp_path):
    make_account("TPL")
    make_categories(tmp_path, "TPLC")
    assert post("TPL", "TPLC", "12.5", "2028-02-29")[0] == 0
    assert parse(cli_runner("txn", "get", "1")[1])[1][4:5] == ["12.50"]


@pytest.mark.parametrize("memo", ["m" * 61, "has,comma"])
def test_txn_post_rejects_a_bad_memo(store, tmp_path, memo):
    make_account("TPB")
    make_categories(tmp_path, "TPBC")
    assert post("TPB", "TPBC", "1.00", memo=memo)[:2] == (3, "")
    assert table_counts()[2] == 0


def test_a_rejected_post_consumes_no_transaction_id(store, tmp_path):
    make_account("TPQ")
    make_categories(tmp_path, "TPQC")
    assert post("TPQ", "TPQC", "1.234")[0] == 3
    assert parse(post("TPQ", "TPQC", "1.00")[1])[1][0] == "1"


@pytest.mark.parametrize("args", [("txn", "post"), ("txn", "post", "A", "B", "1.00"),
                                  ("txn", "post", "A", "B", "1.00", "2026-04-01", "m", "x")])
def test_txn_post_wrong_argument_count_is_usage_error(store, args):
    assert cli_runner(*args)[:2] == (2, "")


def test_txn_get_prints_the_stored_row_with_a_two_decimal_amount(store, tmp_path):
    make_account("TGA")
    make_categories(tmp_path, "TGC")
    assert post("TGA", "TGC", "20.00", "2026-04-01")[0] == 0
    assert post("TGA", "TGC", "-12.50", "2026-04-02")[0] == 0
    assert cli_runner("txn", "get", "2") == (0, "txn_id,date,account,category,amount,memo\n2,2026-04-02,TGA,TGC,-12.50,\n", "")


def test_txn_get_absent_is_not_found(store):
    assert cli_runner("txn", "get", "999")[:2] == (4, "")


@pytest.mark.parametrize("args", [("txn", "get"), ("txn", "get", "1", "2"), ("txn", "get", "abc")])
def test_txn_get_usage_errors(store, args):
    assert cli_runner(*args)[:2] == (2, "")


def test_txn_delete_removes_the_row_and_prints_the_id(store, tmp_path):
    make_account("TDA")
    make_categories(tmp_path, "TDC")
    post("TDA", "TDC", "54.50", memo="gone")
    assert cli_runner("txn", "delete", "1") == (0, "deleted\n1\n", "")
    assert cli_runner("txn", "get", "1")[0] == 4


def test_txn_delete_of_a_credit_that_funds_a_debit_is_rejected(store, tmp_path):
    make_account("TDO")
    make_categories(tmp_path, "TDOC")
    post("TDO", "TDOC", "100.00")
    post("TDO", "TDOC", "-50.00")
    assert cli_runner("txn", "delete", "1")[:2] == (3, "")
    assert table_counts()[2] == 2


def test_txn_delete_of_a_debit_is_accepted(store, tmp_path):
    make_account("TDD")
    make_categories(tmp_path, "TDDC")
    post("TDD", "TDDC", "100.00")
    post("TDD", "TDDC", "-50.00")
    assert cli_runner("txn", "delete", "2")[0] == 0
    assert balance_of("TDD") == "100.00"


def test_txn_delete_absent_is_not_found(store):
    assert cli_runner("txn", "delete", "999")[:2] == (4, "")


def test_txn_amend_changes_only_the_amount(store, tmp_path):
    make_account("TAA")
    make_categories(tmp_path, "TAC")
    post("TAA", "TAC", "45.50", "2026-04-01", "walk in sale")
    assert cli_runner("txn", "amend", "1", "54.50") == (
        0, "txn_id,date,account,category,amount,memo\n1,2026-04-01,TAA,TAC,54.50,walk in sale\n", "")
    assert balance_of("TAA") == "54.50"


def test_txn_amend_that_would_overdraw_is_rejected_and_changes_nothing(store, tmp_path):
    make_account("TAO")
    make_categories(tmp_path, "TAOC")
    post("TAO", "TAOC", "100.00")
    post("TAO", "TAOC", "-50.00")
    assert cli_runner("txn", "amend", "2", "-200.00")[:2] == (3, "")
    assert balance_of("TAO") == "50.00"


def test_txn_amend_to_exactly_zero_is_accepted(store, tmp_path):
    make_account("TAZ")
    make_categories(tmp_path, "TAZC")
    post("TAZ", "TAZC", "100.00")
    post("TAZ", "TAZC", "-50.00")
    assert cli_runner("txn", "amend", "2", "-100.00")[0] == 0
    assert balance_of("TAZ") == "0.00"


@pytest.mark.parametrize("amount", ["1.234", "0", "0.00", "abc", "12."])
def test_txn_amend_rejects_an_invalid_amount_and_keeps_the_row(store, tmp_path, amount):
    make_account("TAI")
    make_categories(tmp_path, "TAIC")
    post("TAI", "TAIC", "20.00", memo="keep")
    assert cli_runner("txn", "amend", "1", amount)[:2] == (3, "")
    assert balance_of("TAI") == "20.00"


def test_txn_amend_absent_is_not_found(store):
    assert cli_runner("txn", "amend", "999", "5.00")[:2] == (4, "")


@pytest.mark.parametrize("args", [("txn", "amend"), ("txn", "amend", "1"),
                                  ("txn", "amend", "1", "2.00", "3.00"), ("txn", "amend", "abc", "2.00")])
def test_txn_amend_usage_errors(store, args):
    assert cli_runner(*args)[:2] == (2, "")


# transfer

def _funded(tmp_path: Path, src: str, dst: str, funds: str = "100.00") -> None:
    make_account(src)
    make_account(dst)
    make_categories(tmp_path, "OPEN", "TRANSFER")
    assert post(src, "OPEN", funds, "2026-04-01")[0] == 0


def test_transfer_writes_two_transfer_rows_with_consecutive_ids(store, tmp_path):
    _funded(tmp_path, "XSRC", "XDST")
    code, out, _ = cli_runner("transfer", "XSRC", "XDST", "25.00", "2026-04-03")
    assert code == 0
    assert parse(out) == [
        TXN_HEADER,
        ["2", "2026-04-03", "XSRC", "TRANSFER", "-25.00", "transfer to XDST"],
        ["3", "2026-04-03", "XDST", "TRANSFER", "25.00", "transfer from XSRC"],
    ]
    assert balance_of("XSRC") == "75.00"
    assert balance_of("XDST") == "25.00"


def test_transfer_of_the_entire_balance_leaves_the_source_at_zero(store, tmp_path):
    _funded(tmp_path, "XSE", "XDE")
    assert cli_runner("transfer", "XSE", "XDE", "100.00", "2026-04-03")[0] == 0
    assert balance_of("XSE") == "0.00"


def test_transfer_larger_than_the_source_balance_writes_neither_row(store, tmp_path):
    _funded(tmp_path, "XSO", "XDO")
    assert cli_runner("transfer", "XSO", "XDO", "100.01", "2026-04-03")[:2] == (3, "")
    assert table_counts()[2] == 1
    assert balance_of("XDO") == "0.00"


@pytest.mark.parametrize("args", [
    ("XSR", "XDS", "0", "2026-04-03"),
    ("XSR", "XDS", "0.00", "2026-04-03"),
    ("XSR", "XDS", "-5.00", "2026-04-03"),
    ("XSR", "XDS", "1.234", "2026-04-03"),
    ("XSR", "XDS", "abc", "2026-04-03"),
    ("XSR", "XSR", "5.00", "2026-04-03"),
    ("XSR", "XNONE", "5.00", "2026-04-03"),
    ("XNONE", "XDS", "5.00", "2026-04-03"),
    ("XSR", "XDS", "5.00", "2026-02-30"),
])
def test_transfer_rejects_bad_input_and_writes_nothing(store, tmp_path, args):
    _funded(tmp_path, "XSR", "XDS")
    before = table_counts()[2]
    assert cli_runner("transfer", *args)[:2] == (3, "")
    assert table_counts()[2] == before


def test_transfer_without_the_transfer_category_is_an_operational_failure(store):
    make_account("XNC1")
    make_account("XNC2")
    assert cli_runner("transfer", "XNC1", "XNC2", "1.00", "2026-04-03")[:2] == (1, "")


@pytest.mark.parametrize("args", [("transfer",), ("transfer", "A", "B", "1.00"),
                                  ("transfer", "A", "B", "1.00", "2026-04-03", "extra")])
def test_transfer_wrong_argument_count_is_usage_error(store, args):
    assert cli_runner(*args)[:2] == (2, "")


# report

def test_report_balances_lists_each_account_in_code_order_then_a_total(store, tmp_path):
    make_account("RPTA")
    make_account("RPTB")
    make_categories(tmp_path, "RPTC")
    post("RPTA", "RPTC", "10.00")
    post("RPTA", "RPTC", "-2.50")
    assert cli_runner("report", "balances") == (0, (
        "account,name,transactions,balance\n"
        "RPTA,Name RPTA,2,7.50\n"
        "RPTB,Name RPTB,0,0.00\n"
        "TOTAL,,2,7.50\n"), "")


def test_report_balances_on_an_empty_store_is_a_zero_total(store):
    assert cli_runner("report", "balances")[1] == "account,name,transactions,balance\nTOTAL,,0,0.00\n"


def test_report_monthly_groups_by_month_and_skips_months_without_rows(store, tmp_path):
    make_account("RMA")
    make_categories(tmp_path, "RMC")
    post("RMA", "RMC", "500.00", "2031-07-01")
    post("RMA", "RMC", "-19.99", "2031-07-15")
    post("RMA", "RMC", "-0.01", "2031-07-20")
    post("RMA", "RMC", "-20.00", "2031-09-02")
    assert cli_runner("report", "monthly")[1] == (
        "month,transactions,inflow,outflow,net\n"
        "2031-07,3,500.00,20.00,480.00\n"
        "2031-09,1,0.00,20.00,-20.00\n"
        "TOTAL,4,500.00,40.00,460.00\n")


def test_report_categories_includes_unused_categories_and_signs_outflow_positive(store, tmp_path):
    make_account("RCA")
    make_categories(tmp_path, "RCX", "RCY", "RCZ")
    post("RCA", "RCX", "90.00")
    post("RCA", "RCY", "-12.34")
    assert cli_runner("report", "categories")[1] == (
        "category,description,transactions,inflow,outflow,net\n"
        "RCX,Desc RCX,1,90.00,0.00,90.00\n"
        "RCY,Desc RCY,1,0.00,12.34,-12.34\n"
        "RCZ,Desc RCZ,0,0.00,0.00,0.00\n"
        "TOTAL,,2,90.00,12.34,77.66\n")


@pytest.mark.parametrize("args", [("report", "nosuch"), ("report", "balances", "extra")])
def test_report_unknown_or_extra_arguments_are_usage_errors(store, args):
    assert cli_runner(*args)[:2] == (2, "")


# seed files load through the public load command

def test_seed_files_load_and_the_bad_file_is_rejected_without_changes(store):
    assert cli_runner("load", "accounts", str(SOURCES / "seed_accounts.csv"))[0] == 0
    assert cli_runner("load", "categories", str(SOURCES / "seed_categories.csv"))[0] == 0
    assert cli_runner("load", "transactions", str(SOURCES / "seed_transactions.csv")) == (
        0, "table,loaded\ntransactions,120\n", "")
    assert table_counts() == [4, 7, 120]
    assert cli_runner("load", "transactions", str(SOURCES / "seed_transactions_bad.csv"))[:2] == (3, "")
    assert table_counts() == [4, 7, 120]
