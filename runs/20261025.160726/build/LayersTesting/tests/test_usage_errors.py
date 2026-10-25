"""Usage errors: unknown commands, unknown targets, and wrong argument counts exit 2.

A usage error is decided from the argument vector alone. Each test checks the exit status, that
standard output is empty, that standard error holds exactly one line, and that the store and any
named file were never touched.
"""

import pytest

from cli.testing import cli_runner


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ledger.db"))
    return tmp_path / "ledger.db"


def assert_usage_error(args: tuple[str, ...]) -> None:
    code, out, err = cli_runner(*args)
    assert code == 2, args
    assert out == "", args
    assert len(err.strip().splitlines()) == 1, args


@pytest.mark.parametrize(
    "args",
    [
        ("frobnicate",),
        ("frobnicate", "extra"),
        ("INIT",),
        ("account",),
        ("txn",),
    ],
)
def test_unknown_or_incomplete_command_is_a_usage_error(store, args):
    assert_usage_error(args)
    assert not store.exists()


def test_no_arguments_is_a_usage_error(store):
    assert_usage_error(())
    assert not store.exists()


@pytest.mark.parametrize("table", ["nosuch", "Accounts", "transaction", ""])
def test_unknown_load_table_is_a_usage_error_even_when_the_file_is_missing(store, table, tmp_path):
    missing = str(tmp_path / "absent.csv")
    code, out, err = cli_runner("load", table, missing)
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert not store.exists()


@pytest.mark.parametrize("report", ["nosuch", "Balances", "monthlies"])
def test_unknown_report_is_a_usage_error(store, report):
    assert_usage_error(("report", report))
    assert not store.exists()


@pytest.mark.parametrize("subcommand", ["frobnicate", "Add", "remove"])
def test_unknown_account_subcommand_is_a_usage_error(store, subcommand):
    assert_usage_error(("account", subcommand))


@pytest.mark.parametrize("subcommand", ["frobnicate", "Post", "update"])
def test_unknown_txn_subcommand_is_a_usage_error(store, subcommand):
    assert_usage_error(("txn", subcommand))


@pytest.mark.parametrize(
    "args",
    [
        ("init", "extra"),
        ("count", "extra"),
        ("load",),
        ("load", "accounts"),
        ("load", "accounts", "a.csv", "b.csv"),
        ("load", "categories"),
        ("load", "transactions", "a.csv", "b.csv"),
        ("account", "add"),
        ("account", "add", "ONLYCODE"),
        ("account", "add", "CODE", "Name", "extra"),
        ("account", "get"),
        ("account", "get", "A", "B"),
        ("account", "rename", "CODE"),
        ("account", "rename", "CODE", "Name", "extra"),
        ("account", "delete"),
        ("account", "delete", "A", "B"),
        ("txn", "post", "ACCT", "CAT", "1.00"),
        ("txn", "post", "ACCT", "CAT", "1.00", "2026-04-01", "memo", "extra"),
        ("txn", "get"),
        ("txn", "get", "1", "2"),
        ("txn", "amend", "1"),
        ("txn", "amend", "1", "2.00", "extra"),
        ("txn", "delete"),
        ("txn", "delete", "1", "2"),
        ("transfer", "FROM", "TO", "1.00"),
        ("transfer", "FROM", "TO", "1.00", "2026-04-01", "extra"),
        ("report",),
        ("report", "balances", "extra"),
        ("report", "monthly", "extra"),
        ("report", "categories", "extra"),
    ],
)
def test_wrong_argument_count_is_a_usage_error_and_touches_nothing(store, args):
    assert_usage_error(args)
    assert not store.exists()


def test_wrong_argument_count_never_reads_a_named_file(store, tmp_path):
    code, out, _ = cli_runner("load", "accounts", str(tmp_path), "extra")
    assert code == 2
    assert out == ""
    assert not store.exists()


def test_correct_argument_count_is_not_a_usage_error(store):
    assert cli_runner("init")[0] == 0
    code, out, _ = cli_runner("account", "get", "NOPE01")
    assert code == 4
    assert out == ""
