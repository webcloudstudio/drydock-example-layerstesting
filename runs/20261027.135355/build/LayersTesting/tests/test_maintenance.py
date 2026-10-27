"""``ledger init`` and ``ledger count``: fresh stores, emptying, counting, and usage errors."""

import csv
import io

import pytest

from cli.testing import cli_runner


def _counts(out: str) -> list[int]:
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
    return [int(row[1]) for row in rows[1:]]


def _seed_one_of_each(path, store_open):
    with store_open(path) as db:
        db.accounts.create(account="ZZMA1", name="Maint Probe")
        db.categories.create(category="ZZMC1", description="Maint Cat")
        db.transactions.create(txn_id=910000001, date="2026-05-01", account="ZZMA1",
                               category="ZZMC1", amount=100, memo="")


def test_init_creates_missing_store_and_schema(tmp_path, monkeypatch):
    path = tmp_path / "fresh.db"
    monkeypatch.setenv("DATABASE_URL", str(path))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert not path.exists()
    code, out, err = cli_runner("init")
    assert code == 0, err
    assert out == ""
    assert path.exists()
    code, out, err = cli_runner("count")
    assert code == 0, err
    assert _counts(out) == [0, 0, 0]


def test_init_on_empty_ledger_exits_zero_again(ledger_store):
    for _ in range(2):
        code, out, err = cli_runner("init")
        assert code == 0, err
        assert out == ""


def test_init_removes_every_row_from_all_three_tables(ledger_store, store_open):
    _seed_one_of_each(ledger_store, store_open)
    code, out, err = cli_runner("init")
    assert code == 0, err
    assert out == ""
    with store_open(ledger_store) as db:
        assert db.transactions.list() == []
        assert db.categories.list() == []
        assert db.accounts.list() == []


def test_init_leaves_no_rows_even_with_many_stored(ledger_store, store_open):
    with store_open(ledger_store) as db:
        for i in range(25):
            db.accounts.create(account=f"ZZMM{i:02d}", name="Many")
            db.categories.create(category=f"ZZMK{i:02d}", description="Many")
            db.transactions.create(txn_id=920000000 + i, date="2026-05-01", account=f"ZZMM{i:02d}",
                                   category=f"ZZMK{i:02d}", amount=100, memo="")
    code, _, err = cli_runner("init")
    assert code == 0, err
    code, out, err = cli_runner("count")
    assert code == 0, err
    assert _counts(out) == [0, 0, 0]


def test_count_reports_zero_on_empty_ledger(ledger_store):
    code, out, err = cli_runner("count")
    assert code == 0, err
    assert _counts(out) == [0, 0, 0]


def test_count_reports_each_stored_row(ledger_store, store_open):
    _seed_one_of_each(ledger_store, store_open)
    code, out, err = cli_runner("count")
    assert code == 0, err
    assert _counts(out) == [1, 1, 1]


def test_count_rises_by_one_per_write(ledger_store, store_open):
    code, out, _ = cli_runner("count")
    before = _counts(out)
    _seed_one_of_each(ledger_store, store_open)
    code, out, err = cli_runner("count")
    assert code == 0, err
    assert _counts(out) == [n + 1 for n in before]


def test_count_is_read_from_the_store_each_run(ledger_store, store_open):
    code, out, _ = cli_runner("count")
    assert _counts(out) == [0, 0, 0]
    with store_open(ledger_store) as db:
        db.accounts.create(account="ZZMC2", name="Later")
    code, out, _ = cli_runner("count")
    assert _counts(out) == [1, 0, 0]


@pytest.mark.parametrize("command", ["init", "count"])
def test_extra_argument_is_usage_error(ledger_store, command):
    code, out, _ = cli_runner(command, "extra")
    assert code == 2
    assert out == ""


def test_init_does_not_create_a_missing_parent_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "absent" / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    code, out, _ = cli_runner("init")
    assert code == 1
    assert out == ""
    assert not (tmp_path / "absent").exists()


def test_init_creates_schema_on_fresh_store_inside_acceptance_transaction(tmp_path, monkeypatch):
    from persistence.db import begin_acceptance_transaction, end_acceptance_transaction

    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "fresh.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    begin_acceptance_transaction()
    try:
        code, out, err = cli_runner("init")
        assert code == 0, err
        assert out == ""
        code, out, err = cli_runner("count")
        assert code == 0, err
        assert _counts(out) == [0, 0, 0]
    finally:
        end_acceptance_transaction()
