"""CLI foundation: executable, dispatch, exit codes, CSV output, validators, and money.

Each declared acceptance assertion of FEATURE-CliFoundation has a test here, read back through the
public interface. Finer tests cover the boundaries and the dispatch and output rules.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from cli import errors
from cli.database import database_location, open_ledger
from cli.errors import LedgerError, Rejected
from cli.money import format_amount, parse_amount
from cli.output import TRANSACTION_HEADER, format_transaction, write_rows
from cli.registry import COMMANDS, Command, register, resolve
from cli.testing import cli_runner
from cli.validate import validate_code, validate_date, validate_memo, validate_name
from persistence import Database, PersistenceError

APP_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def scratch_command(monkeypatch):
    """Register one throwaway command for a test and remove it afterwards."""

    def add(path, min_args, max_args, handler):
        monkeypatch.setitem(COMMANDS, tuple(path), Command(tuple(path), min_args, max_args, handler))

    return add


# ── Executable and process-level behavior ───────────────────────────────────────────────────


def test_ledger_executable_exists_at_application_root():
    assert (APP_ROOT / "ledger").is_file()
    assert os.access(APP_ROOT / "ledger", os.X_OK)


def test_ledger_with_unknown_command_exits_2_and_writes_no_stdout():
    result = subprocess.run(
        [str(APP_ROOT / "ledger"), "frobnicate"],
        capture_output=True,
        text=True,
        env={**os.environ},
        cwd=APP_ROOT,
    )
    assert result.returncode == 2
    assert result.stdout == ""


# ── Usage errors ────────────────────────────────────────────────────────────────────────────


def test_unknown_report_exits_2_with_no_stdout():
    code, out, _ = cli_runner("report", "nosuchreport")
    assert code == 2
    assert out == ""


def test_unknown_table_load_exits_2_with_no_stdout():
    code, out, _ = cli_runner("load", "nosuchtable", "missing.csv")
    assert code == 2
    assert out == ""


def test_wrong_argument_count_exits_2_with_no_stdout(scratch_command):
    scratch_command(("account", "get"), 1, 1, lambda db, args: [["x"]])
    scratch_command(("count",), 0, 0, lambda db, args: [["x"]])
    code, out, _ = cli_runner("account", "get")
    assert (code, out) == (2, "")
    code, out, _ = cli_runner("count", "extra")
    assert (code, out) == (2, "")


def test_no_command_exits_2_with_no_stdout():
    code, out, _ = cli_runner()
    assert code == 2
    assert out == ""


def test_usage_error_writes_one_line_to_stderr_only():
    code, out, err = cli_runner("frobnicate")
    assert code == 2
    assert out == ""
    assert err.count("\n") == 1


# ── Dispatch ────────────────────────────────────────────────────────────────────────────────


def test_resolve_matches_the_longest_registered_path(scratch_command):
    scratch_command(("account",), 0, 9, lambda db, args: [])
    scratch_command(("account", "get"), 1, 1, lambda db, args: [])
    command, args = resolve(["account", "get", "DRAWER1"])
    assert command.path == ("account", "get")
    assert args == ["DRAWER1"]


def test_register_rejects_a_duplicate_path(scratch_command):
    scratch_command(("dup",), 0, 0, lambda db, args: [])
    with pytest.raises(ValueError):
        register(("dup",), 0, 0, lambda db, args: [])


def test_register_rejects_an_empty_path():
    with pytest.raises(ValueError):
        register((), 0, 0, lambda db, args: [])


def test_handler_receives_the_open_database_and_its_arguments(scratch_command, monkeypatch, tmp_path):
    seen = {}

    def handler(db, args):
        seen["db"] = db
        seen["args"] = args
        return [["h"]]

    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    scratch_command(("probe",), 1, 2, handler)
    code, out, _ = cli_runner("probe", "A", "B")
    assert code == 0
    assert isinstance(seen["db"], Database)
    assert seen["args"] == ["A", "B"]


def test_handler_rows_are_written_as_csv_on_success(scratch_command, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    scratch_command(("rows",), 0, 0, lambda db, args: [["a", "b"], ["1", "2"]])
    code, out, err = cli_runner("rows")
    assert code == 0
    assert out == "a,b\n1,2\n"
    assert err == ""


def test_handler_error_exits_with_its_code_and_writes_nothing(scratch_command, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))

    def handler(db, args):
        raise errors.NotFound("no such account")

    scratch_command(("fail",), 0, 0, handler)
    code, out, _ = cli_runner("fail")
    assert code == 4
    assert out == ""


def test_persistence_failure_exits_1_and_writes_nothing(scratch_command, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))

    def handler(db, args):
        raise PersistenceError("store unavailable")

    scratch_command(("broken",), 0, 0, handler)
    code, out, _ = cli_runner("broken")
    assert code == 1
    assert out == ""


# ── Exit codes ──────────────────────────────────────────────────────────────────────────────


def test_error_classes_carry_exit_codes_1_2_3_and_4():
    assert issubclass(errors.Operational, errors.LedgerError)
    assert issubclass(errors.Usage, errors.LedgerError)
    assert issubclass(errors.Rejected, errors.LedgerError)
    assert issubclass(errors.NotFound, errors.LedgerError)
    assert errors.Operational("x").exit_code == 1
    assert errors.Usage("x").exit_code == 2
    assert errors.Rejected("x").exit_code == 3
    assert errors.NotFound("x").exit_code == 4


def test_ledger_error_base_is_an_exception_with_default_exit_code_1():
    assert LedgerError.exit_code == 1
    assert issubclass(LedgerError, Exception)


# ── Money ───────────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("text", ["5000.00", "-12.50", "45.07"])
def test_amount_round_trips_through_integer_cents(text):
    cents = parse_amount(text)
    assert isinstance(cents, int)
    assert format_amount(cents) == text


def test_amount_parses_to_exact_cents():
    assert parse_amount("5000.00") == 500000
    assert parse_amount("-12.50") == -1250
    assert parse_amount("45.07") == 4507


@pytest.mark.parametrize(
    ("short", "padded"), [("12.5", "12.50"), ("7", "7.00"), ("-3.1", "-3.10")]
)
def test_amount_short_forms_equal_their_padded_form(short, padded):
    assert parse_amount(short) == parse_amount(padded)


@pytest.mark.parametrize("text", ["0", "0.00", "-0", "1.234", "abc", "", "1,00", "+5.00", ".5"])
def test_amount_rejections_exit_with_code_3(text):
    with pytest.raises(Rejected) as caught:
        parse_amount(text)
    assert caught.value.exit_code == 3


def test_format_amount_has_two_decimals_and_no_separator():
    assert format_amount(0) == "0.00"
    assert format_amount(5) == "0.05"
    assert format_amount(-5) == "-0.05"
    assert format_amount(123456789) == "1234567.89"


# ── Validators ──────────────────────────────────────────────────────────────────────────────


def test_valid_date_is_returned_unchanged():
    assert validate_date("2026-02-28") == "2026-02-28"


@pytest.mark.parametrize("bad", ["2026-02-30", "2026-13-01", "26-01-01", "2026/01/01", "", "20260101"])
def test_invalid_dates_are_rejected(bad):
    with pytest.raises(Rejected):
        validate_date(bad)


@pytest.mark.parametrize("good", ["A", "DRAWER1", "ABCDEFGHIJKL"])
def test_codes_of_one_to_twelve_characters_are_accepted(good):
    assert validate_code(good) == good


@pytest.mark.parametrize("bad", ["", "lower", "ABCDEFGHIJKLM", "A-B", "A B", "A\n"])
def test_invalid_codes_are_rejected(bad):
    with pytest.raises(Rejected):
        validate_code(bad)


def test_name_boundaries_are_accepted():
    assert validate_name("Front Drawer") == "Front Drawer"
    assert validate_name("n" * 40) == "n" * 40


@pytest.mark.parametrize("bad", ["", "n" * 41, "a,b", "a\nb", "a\rb"])
def test_invalid_names_are_rejected(bad):
    with pytest.raises(Rejected):
        validate_name(bad)


def test_memo_boundaries_are_accepted():
    assert validate_memo("") == ""
    assert validate_memo("m" * 60) == "m" * 60


@pytest.mark.parametrize("bad", ["m" * 61, "a,b", "a\nb"])
def test_invalid_memos_are_rejected(bad):
    with pytest.raises(Rejected):
        validate_memo(bad)


# ── CSV output and transaction rows ─────────────────────────────────────────────────────────


def test_transaction_row_formats_to_six_csv_fields():
    row = SimpleNamespace(
        txn_id=77, date="2026-04-01", account="DRAWER1", category="SALES", amount=4550, memo="walk in"
    )
    assert list(TRANSACTION_HEADER) == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert format_transaction(row) == ["77", "2026-04-01", "DRAWER1", "SALES", "45.50", "walk in"]


def test_empty_memo_leaves_a_trailing_empty_field():
    row = SimpleNamespace(txn_id=1, date="2026-04-01", account="A", category="B", amount=-100, memo="")
    assert format_transaction(row)[-1] == ""


def test_write_rows_joins_fields_with_commas_and_newlines(capsys):
    write_rows([["a", "b"], ["c", ""]])
    assert capsys.readouterr().out == "a,b\nc,\n"


def test_write_rows_writes_nothing_for_no_rows(capsys):
    write_rows([])
    assert capsys.readouterr().out == ""


# ── Store location ──────────────────────────────────────────────────────────────────────────


def test_database_url_takes_precedence(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "/tmp/url.db")
    monkeypatch.setenv("DATABASE_PATH", "/tmp/path.db")
    assert database_location() == "/tmp/url.db"


def test_database_path_is_used_when_url_is_unset(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", "/tmp/path.db")
    assert database_location() == "/tmp/path.db"


def test_default_database_path_is_data_app_db(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert database_location() == "data/app.db"


def test_open_ledger_returns_the_shipped_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    with open_ledger() as db:
        assert isinstance(db, Database)
