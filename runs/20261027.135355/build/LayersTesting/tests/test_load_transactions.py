"""``ledger load transactions``: all-or-nothing loads with validation and the balance rule checked first."""

import csv
import io
from decimal import Decimal

import pytest

from cli.testing import cli_runner
from persistence import PersistenceError
from persistence import db as persistence_db

HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
ACCT = "ZTA1"
CAT = "ZTC1"


def _write(path, rows, header=HEADER) -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return str(path)


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _cents(text: str) -> int:
    return int(Decimal(text) * 100)


@pytest.fixture
def seeded(ledger_store, store_open):
    """Create the account and category the rows reference, and return the store path."""
    with store_open(ledger_store) as db:
        db.accounts.create(account=ACCT, name="Txn Load Account")
        db.categories.create(category=CAT, description="Txn Load Category")
    return ledger_store


def _stored(store_open, path) -> dict[int, tuple]:
    with store_open(path) as db:
        return {
            row.txn_id: (row.date, row.account, row.category, row.amount, row.memo)
            for row in db.transactions.list()
        }


# ── success ───────────────────────────────────────────────────────────────────────────────


def test_load_reports_count_and_keeps_file_txn_ids(seeded, store_open, tmp_path):
    rows = [
        ["920000001", "2026-01-02", ACCT, CAT, "100.50", "deposit"],
        ["920000002", "2026-01-03", ACCT, CAT, "-20.25", "withdrawal"],
        ["920000003", "2026-01-04", ACCT, CAT, "7", ""],
    ]
    path = _write(tmp_path / "txns.csv", rows)
    code, out, err = cli_runner("load", "transactions", path)
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["transactions", "3"]]
    stored = _stored(store_open, seeded)
    for txn_id, day, account, category, amount, memo in rows:
        assert stored[int(txn_id)] == (day, account, category, _cents(amount), memo)


def test_load_header_only_loads_zero_rows(seeded, tmp_path):
    path = _write(tmp_path / "txns.csv", [])
    code, out, err = cli_runner("load", "transactions", path)
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["transactions", "0"]]


def test_load_accepts_memo_of_exactly_sixty_characters(seeded, store_open, tmp_path):
    memo = "m" * 60
    path = _write(tmp_path / "txns.csv", [["920000010", "2026-01-05", ACCT, CAT, "1.00", memo]])
    code, _, err = cli_runner("load", "transactions", path)
    assert code == 0, err
    assert _stored(store_open, seeded)[920000010][4] == memo


def test_load_accepts_one_decimal_amount_and_a_withdrawal_that_leaves_zero(seeded, store_open, tmp_path):
    rows = [["920000011", "2026-01-05", ACCT, CAT, "5.5", ""], ["920000012", "2026-01-06", ACCT, CAT, "-5.50", ""]]
    code, _, err = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 0, err
    stored = _stored(store_open, seeded)
    assert stored[920000011][3] == 550
    assert stored[920000012][3] == -550


def test_load_balance_considers_whole_file_withdrawal_before_deposit(seeded, store_open, tmp_path):
    rows = [
        ["920000500", "2026-08-01", ACCT, CAT, "-3.00", "withdraw first"],
        ["920000501", "2026-08-02", ACCT, CAT, "5.00", "deposit second"],
    ]
    code, out, err = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 0, err
    assert _rows(out) == [["table", "loaded"], ["transactions", "2"]]
    assert len(_stored(store_open, seeded)) == 2


# ── balance rule ──────────────────────────────────────────────────────────────────────────


def test_load_rejects_file_whose_net_effect_overdraws_and_stores_nothing(seeded, store_open, tmp_path):
    rows = [
        ["920000400", "2026-07-01", ACCT, CAT, "1.00", "deposit"],
        ["920000401", "2026-07-02", ACCT, CAT, "-2.00", "overdraw"],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_rejects_overdraft_against_stored_balance(seeded, store_open, tmp_path):
    with store_open(seeded) as db:
        db.transactions.create(txn_id=920000450, date="2026-07-01", account=ACCT, category=CAT, amount=500, memo="")
    rows = [["920000451", "2026-07-02", ACCT, CAT, "-5.01", ""]]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    assert set(_stored(store_open, seeded)) == {920000450}


# ── foreign keys ──────────────────────────────────────────────────────────────────────────


def test_load_unknown_account_rejects_whole_file(seeded, store_open, tmp_path):
    rows = [["920000100", "2026-04-01", ACCT, CAT, "10.00", ""], ["920000101", "2026-04-01", "ZTNOPE", CAT, "1.00", ""]]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_unknown_category_rejects_whole_file(seeded, store_open, tmp_path):
    rows = [["920000120", "2026-04-01", ACCT, "ZTNOCAT", "10.00", ""]]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_rejects_row_eleven_and_stores_none_of_the_first_ten(seeded, store_open, tmp_path):
    base = 920000130
    good = [[str(base + i), "2026-04-01", ACCT, CAT, "10.00", f"batch {i}"] for i in range(1, 11)]
    bad = [str(base + 11), "2026-04-01", "ZTNOSUCH", CAT, "10.00", "unknown account"]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", good + [bad]))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


# ── invalid fields ────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "bad",
    [
        ["920000201", "2026-02-30", ACCT, CAT, "10.00", "impossible date"],
        ["920000202", "2026-5-1", ACCT, CAT, "10.00", "short date"],
        ["920000203", "2026-05-01", ACCT, CAT, "1.234", "three decimals"],
        ["920000204", "2026-05-01", ACCT, CAT, "0.00", "zero amount"],
        ["920000205", "2026-05-01", ACCT, CAT, "abc", "not a number"],
        ["920000206", "2026-05-01", ACCT, CAT, "10.00", "m" * 61],
        ["notanumber", "2026-05-01", ACCT, CAT, "10.00", "bad id"],
        ["920000207", "2026-05-01", ACCT, CAT, "10.00", "has,comma"],
    ],
)
def test_load_invalid_row_stores_neither_it_nor_the_valid_row_before_it(seeded, store_open, tmp_path, bad):
    first = ["920000200", "2026-05-01", ACCT, CAT, "10.00", "ok"]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", [first, bad]))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


# ── repeated ids ──────────────────────────────────────────────────────────────────────────


def test_load_rejects_txn_id_repeated_within_file(seeded, store_open, tmp_path):
    rows = [["920000300", "2026-06-01", ACCT, CAT, "5.00", ""], ["920000300", "2026-06-02", ACCT, CAT, "6.00", ""]]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_rejects_txn_id_already_stored_and_leaves_row_unchanged(seeded, store_open, tmp_path):
    with store_open(seeded) as db:
        db.transactions.create(txn_id=920000310, date="2026-06-03", account=ACCT, category=CAT, amount=4321, memo="stored")
    rows = [["920000311", "2026-06-04", ACCT, CAT, "1.00", ""], ["920000310", "2026-06-05", ACCT, CAT, "9.99", "replacement"]]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    assert code == 3
    assert out == ""
    stored = _stored(store_open, seeded)
    assert set(stored) == {920000310}
    assert stored[920000310] == ("2026-06-03", ACCT, CAT, 4321, "stored")


# ── header and usage ──────────────────────────────────────────────────────────────────────


def test_load_wrong_header_stores_nothing(seeded, store_open, tmp_path):
    wrong = ["id", "date", "account", "category", "amount", "memo"]
    path = _write(tmp_path / "txns.csv", [["920000600", "2026-09-01", ACCT, CAT, "1.00", ""]], header=wrong)
    code, out, _ = cli_runner("load", "transactions", path)
    assert code == 3
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_missing_file_exits_one_and_stores_nothing(seeded, store_open, tmp_path):
    code, out, _ = cli_runner("load", "transactions", str(tmp_path / "absent.csv"))
    assert code == 1
    assert out == ""
    assert _stored(store_open, seeded) == {}


def test_load_usage_requires_exactly_one_file(seeded):
    for args in [("load", "transactions"), ("load", "transactions", "a.csv", "b.csv")]:
        code, out, _ = cli_runner(*args)
        assert code == 2
        assert out == ""


# ── atomicity ─────────────────────────────────────────────────────────────────────────────


def test_load_failing_insert_removes_rows_already_stored(seeded, store_open, tmp_path, monkeypatch):
    """A storage failure on the third insert removes the first two, so the file loads nothing."""
    original = persistence_db.Database.run
    creates = []

    def failing_run(self, operation, arguments):
        if operation.identifier == "FEATURE-TXN-001":
            creates.append(arguments["txn_id"])
            if len(creates) == 3:
                raise PersistenceError("simulated write failure")
        return original(self, operation, arguments)

    monkeypatch.setattr(persistence_db.Database, "run", failing_run)
    rows = [
        ["920000700", "2026-10-01", ACCT, CAT, "1.00", ""],
        ["920000701", "2026-10-02", ACCT, CAT, "2.00", ""],
        ["920000702", "2026-10-03", ACCT, CAT, "3.00", ""],
    ]
    code, out, _ = cli_runner("load", "transactions", _write(tmp_path / "txns.csv", rows))
    monkeypatch.undo()
    assert code == 1
    assert out == ""
    assert _stored(store_open, seeded) == {}
