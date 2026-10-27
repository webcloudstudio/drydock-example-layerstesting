"""``ledger load accounts`` and ``ledger load categories``: all-or-nothing bulk loads with read-back."""

import csv
import io

import pytest

from cli.testing import cli_runner
from persistence import db as persistence_db
from persistence import PersistenceError

ACCOUNT_HEADER = ["account", "name"]
CATEGORY_HEADER = ["category", "description"]


def _write(path, header, rows) -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return str(path)


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _accounts(store_open, path):
    with store_open(path) as db:
        return {row.account: row.name for row in db.accounts.list()}


def _categories(store_open, path):
    with store_open(path) as db:
        return {row.category: row.description for row in db.categories.list()}


# ── accounts ──────────────────────────────────────────────────────────────────────────────


def test_accounts_load_reports_count_and_reads_back(ledger_store, store_open, tmp_path):
    rows = [["ZLA1", "Load One"], ["ZLA2", "Load Two"], ["ZLA3", "Load Three"]]
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, rows)
    code, out, err = cli_runner("load", "accounts", path)
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["accounts", "3"]]
    assert _accounts(store_open, ledger_store) == {acct: name for acct, name in rows}


def test_accounts_header_only_loads_zero_rows(ledger_store, tmp_path):
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [])
    code, out, err = cli_runner("load", "accounts", path)
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["accounts", "0"]]


def test_accounts_load_accepts_largest_code_and_name(ledger_store, store_open, tmp_path):
    rows = [["Z" * 12, "n" * 40]]
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, rows)
    code, _, err = cli_runner("load", "accounts", path)
    assert code == 0, err
    assert _accounts(store_open, ledger_store) == {"Z" * 12: "n" * 40}


@pytest.mark.parametrize(
    "bad",
    [
        ["zzlc1", "Lowercase Code"],
        ["ABCDEFGHIJKLM", "Code Too Long"],
        ["ZZ-1", "Bad Character"],
        ["", "Empty Code"],
        ["ZZL9", ""],
        ["ZZL9", "x" * 41],
        ["ZZL9", "has,comma"],
    ],
)
def test_accounts_invalid_row_stores_nothing(ledger_store, store_open, tmp_path, bad):
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [["ZZLX1", "Valid First"], bad])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_duplicate_within_file_stores_nothing(ledger_store, store_open, tmp_path):
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [["ZLD1", "One"], ["ZLD2", "Two"], ["ZLD1", "Again"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_duplicate_of_stored_code_leaves_stored_row_unchanged(ledger_store, store_open, tmp_path):
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZLS1", name="Already Stored")
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [["ZLS2", "Fresh"], ["ZLS1", "Replacement"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert _accounts(store_open, ledger_store) == {"ZLS1": "Already Stored"}


def test_accounts_wrong_header_stores_nothing(ledger_store, store_open, tmp_path):
    path = _write(tmp_path / "accounts.csv", ["code", "name"], [["ZLH1", "Wrong Header"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_row_with_extra_field_stores_nothing(ledger_store, store_open, tmp_path):
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [["ZLF1", "Good"], ["ZLF2", "Too", "Many"]])
    code, out, _ = cli_runner("load", "accounts", path)
    assert code == 3
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_missing_file_exits_one_and_stores_nothing(ledger_store, store_open, tmp_path):
    code, out, _ = cli_runner("load", "accounts", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_failing_insert_removes_rows_already_stored(ledger_store, store_open, tmp_path, monkeypatch):
    """A storage failure on the third insert removes the first two, so the file loads nothing."""
    original = persistence_db.Database.run
    creates = []

    def failing_run(self, operation, arguments):
        if operation.identifier == "FEATURE-ACCOUNT-001":
            creates.append(arguments["account"])
            if len(creates) == 3:
                raise PersistenceError("simulated write failure")
        return original(self, operation, arguments)

    monkeypatch.setattr(persistence_db.Database, "run", failing_run)
    path = _write(tmp_path / "accounts.csv", ACCOUNT_HEADER, [["ZLW1", "One"], ["ZLW2", "Two"], ["ZLW3", "Three"]])
    code, out, _ = cli_runner("load", "accounts", path)
    monkeypatch.undo()
    assert code == 1
    assert out == ""
    assert _accounts(store_open, ledger_store) == {}


def test_accounts_usage_requires_exactly_one_file(ledger_store):
    for args in [("load", "accounts"), ("load", "accounts", "a.csv", "b.csv")]:
        code, out, _ = cli_runner(*args)
        assert code == 2
        assert out == ""


# ── categories ────────────────────────────────────────────────────────────────────────────


def test_categories_load_reports_count_and_reads_back(ledger_store, store_open, tmp_path):
    rows = [["ZLC1", "Cat One"], ["ZLC2", "Cat Two"]]
    path = _write(tmp_path / "categories.csv", CATEGORY_HEADER, rows)
    code, out, err = cli_runner("load", "categories", path)
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["categories", "2"]]
    assert _categories(store_open, ledger_store) == {cat: text for cat, text in rows}


def test_categories_header_only_loads_zero_rows(ledger_store, tmp_path):
    path = _write(tmp_path / "categories.csv", CATEGORY_HEADER, [])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 0
    assert _rows(out) == [["table", "loaded"], ["categories", "0"]]


@pytest.mark.parametrize(
    "bad",
    [
        ["zlk1", "Lowercase"],
        ["ABCDEFGHIJKLM", "Too Long Code"],
        ["", "Empty Code"],
        ["ZLK9", ""],
        ["ZLK9", "x" * 41],
        ["ZLK9", "has,comma"],
    ],
)
def test_categories_invalid_row_stores_nothing(ledger_store, store_open, tmp_path, bad):
    path = _write(tmp_path / "categories.csv", CATEGORY_HEADER, [["ZLKX1", "Valid First"], bad])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert _categories(store_open, ledger_store) == {}


def test_categories_duplicate_of_stored_code_is_rejected(ledger_store, store_open, tmp_path):
    with store_open(ledger_store) as db:
        db.categories.create(category="ZLKS", description="Already Stored")
    path = _write(tmp_path / "categories.csv", CATEGORY_HEADER, [["ZLKF", "Fresh"], ["ZLKS", "Replacement"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert _categories(store_open, ledger_store) == {"ZLKS": "Already Stored"}


def test_categories_duplicate_within_file_is_rejected(ledger_store, store_open, tmp_path):
    path = _write(tmp_path / "categories.csv", CATEGORY_HEADER, [["ZLKD", "One"], ["ZLKD", "Again"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""
    assert _categories(store_open, ledger_store) == {}


def test_categories_wrong_header_is_rejected(ledger_store, tmp_path):
    path = _write(tmp_path / "categories.csv", ["category", "name"], [["ZLKH", "Wrong"]])
    code, out, _ = cli_runner("load", "categories", path)
    assert code == 3
    assert out == ""


def test_categories_usage_requires_exactly_one_file(ledger_store):
    code, out, _ = cli_runner("load", "categories")
    assert code == 2
    assert out == ""

