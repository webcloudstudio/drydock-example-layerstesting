"""Database resolution: DATABASE_URL, then DATABASE_PATH, then data/app.db, and the engine each selects.

The resolver tests are pure. The store tests point the environment at a temporary SQLite file and
read the stored values back through the command layer and the shipped persistence library.
"""

import csv
import io

import pytest

from cli.database import database_engine, resolve_database_dsn
from cli.testing import cli_runner
from persistence import open_database


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    assert cli_runner("init")[0] == 0
    return tmp_path / "ledger.db"


def parse(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out, newline="")))


def test_database_url_takes_precedence_over_database_path():
    url = "postgres://user@host/ledger"
    assert resolve_database_dsn({"DATABASE_URL": url, "DATABASE_PATH": "other/place.db"}) == url


def test_database_url_alone_is_returned_unchanged():
    url = "postgresql://user@host:5432/ledger"
    assert resolve_database_dsn({"DATABASE_URL": url}) == url


def test_database_path_is_used_when_database_url_is_unset():
    assert resolve_database_dsn({"DATABASE_PATH": "other/place.db"}) == "other/place.db"


def test_empty_database_url_counts_as_unset():
    environ = {"DATABASE_URL": "", "DATABASE_PATH": "other/place.db"}
    assert resolve_database_dsn(environ) == "other/place.db"


def test_empty_database_path_counts_as_unset_and_falls_to_default():
    assert resolve_database_dsn({"DATABASE_PATH": ""}) == "data/app.db"


def test_default_is_data_app_db_when_neither_variable_is_set():
    assert resolve_database_dsn({}) == "data/app.db"


def test_resolver_ignores_unrelated_environment_variables():
    assert resolve_database_dsn({"HOME": "/home/x", "SECRET_KEY": "s"}) == "data/app.db"


@pytest.mark.parametrize("dsn", ["postgres://u@h/db", "postgresql://u@h/db", "POSTGRES://u@h/db"])
def test_postgres_prefixes_select_postgres(dsn):
    assert database_engine(dsn) == "postgres"


@pytest.mark.parametrize(
    "dsn",
    ["data/app.db", "sqlite:///tmp/x.db", "/abs/path/ledger.db", "sqlite://data/app.db", "app.db"],
)
def test_anything_else_selects_sqlite(dsn):
    assert database_engine(dsn) == "sqlite"


def test_count_runs_against_the_configured_store_and_lists_three_tables_in_order(store):
    code, out, _ = cli_runner("count")
    assert code == 0
    rows = parse(out)
    assert rows[0] == ["table", "rows"]
    assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
    assert all(row[1].isdigit() for row in rows[1:])


def test_count_reflects_a_row_written_to_the_configured_store(store):
    assert cli_runner("account", "add", "DSNA1", "Count Me")[0] == 0
    rows = parse(cli_runner("count")[1])
    assert rows[1] == ["accounts", "1"]


def test_sqlite_url_prefix_is_honoured_and_creates_its_parent_directory(tmp_path, monkeypatch):
    target = tmp_path / "prefixed" / "ledger.db"
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.setenv("DATABASE_URL", f"sqlite://{target}")
    assert cli_runner("init")[0] == 0
    assert target.is_file()
    assert cli_runner("account", "add", "DSNP1", "Prefixed")[0] == 0
    assert open_database(f"sqlite://{target}").accounts.get(account="DSNP1").name == "Prefixed"


def test_a_posted_amount_is_stored_as_an_integer_number_of_cents(store):
    assert cli_runner("account", "add", "DSNC1", "Cents Account")[0] == 0
    cats = store.parent / "cats.csv"
    cats.write_text("category,description\nDSNCC1,Cents Category\n", encoding="utf-8")
    assert cli_runner("load", "categories", str(cats))[0] == 0

    code, out, _ = cli_runner("txn", "post", "DSNC1", "DSNCC1", "12.34", "2026-06-02", "cents")
    assert code == 0
    txn_id = int(parse(out)[1][0])

    stored = open_database(str(store)).transactions.get(txn_id=txn_id)
    assert stored is not None
    assert isinstance(stored.amount, int)
    assert stored.amount == 1234
