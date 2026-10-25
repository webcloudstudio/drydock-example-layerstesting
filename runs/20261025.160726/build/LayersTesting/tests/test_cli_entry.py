"""Behavior of the cli entry point: dispatch, argument counts, exit codes, CSV output, and DSN resolution.

Every command here is registered under a ``zzt-`` name so it cannot collide with a real command.
"""

import csv
import io
from pathlib import Path

import pytest

from cli.context import open_store
from cli.errors import NotFound, OperationalError, Rejected, UsageError
from cli.registry import register
from cli.testing import cli_runner
from persistence import Database, PersistenceError


def test_unknown_command_exits_2_with_empty_stdout_and_one_diagnostic_line():
    code, out, err = cli_runner("zzt-no-such-command")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_no_arguments_is_a_usage_error():
    code, out, _ = cli_runner()
    assert code == 2
    assert out == ""


def test_rows_are_written_as_unquoted_csv_with_lf_endings():
    rows = [["h1", "h2"], ["v1", "v2"]]
    register(("zzt-csv",), lambda args: rows, (0, 0))
    code, out, _ = cli_runner("zzt-csv")
    assert code == 0
    assert out == "h1,h2\nv1,v2\n"
    assert "\r" not in out


def test_rows_round_trip_through_csv_reader():
    rows = [["a", "b", "c"], ["1", "", "3"]]
    register(("zzt-roundtrip",), lambda args: rows, (0, 0))
    _, out, _ = cli_runner("zzt-roundtrip")
    assert list(csv.reader(io.StringIO(out, newline=""))) == rows


def test_fields_are_not_quoted_even_when_they_contain_a_comma():
    register(("zzt-unquoted",), lambda args: [["a,b", "c"]], (0, 0))
    _, out, _ = cli_runner("zzt-unquoted")
    assert out == "a,b,c\n"


def test_handler_returning_none_exits_0_with_no_output():
    register(("zzt-none",), lambda args: None, (0, 0))
    code, out, err = cli_runner("zzt-none")
    assert code == 0
    assert out == ""
    assert err == ""


def test_handler_returning_no_rows_exits_0_with_no_output():
    register(("zzt-empty",), lambda args: [], (0, 0))
    code, out, _ = cli_runner("zzt-empty")
    assert code == 0
    assert out == ""


def test_handler_receives_the_arguments_after_its_words():
    seen = []

    def handler(args):
        seen.append(list(args))
        return None

    register(("zzt-args",), handler, (0, 3))
    assert cli_runner("zzt-args")[0] == 0
    assert cli_runner("zzt-args", "x", "y")[0] == 0
    assert seen == [[], ["x", "y"]]


@pytest.mark.parametrize(
    "exc, code",
    [(Rejected, 3), (NotFound, 4), (OperationalError, 1), (UsageError, 2)],
)
def test_ledger_error_maps_to_its_exit_code_with_one_diagnostic_line(exc, code):
    def handler(args):
        raise exc("diagnostic")

    name = f"zzt-err-{code}"
    register((name,), handler, (0, 0))
    got, out, err = cli_runner(name)
    assert got == code
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_unexpected_exception_maps_to_exit_1_with_empty_stdout():
    def boom(args):
        raise RuntimeError("unexpected")

    register(("zzt-boom",), boom, (0, 0))
    code, out, err = cli_runner("zzt-boom")
    assert code == 1
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_persistence_error_maps_to_exit_1_with_empty_stdout():
    def fail(args):
        raise PersistenceError("store unreachable")

    register(("zzt-persist",), fail, (0, 0))
    code, out, err = cli_runner("zzt-persist")
    assert code == 1
    assert out == ""
    assert "store unreachable" in err


def test_failing_handler_writes_nothing_to_stdout_even_after_partial_work():
    def partial(args):
        raise Rejected("refused before any row was produced")

    register(("zzt-partial",), partial, (0, 0))
    code, out, _ = cli_runner("zzt-partial")
    assert code == 3
    assert out == ""


def test_diagnostic_is_one_line_even_when_the_message_spans_lines():
    def multi(args):
        raise Rejected("first line\nsecond line")

    register(("zzt-multiline",), multi, (0, 0))
    _, _, err = cli_runner("zzt-multiline")
    assert len(err.strip().splitlines()) == 1


def test_argument_count_below_minimum_is_usage_error_and_handler_not_called():
    calls = []

    def handler(args):
        calls.append(list(args))
        return [["x"]]

    register(("zzt-one",), handler, (1, 1))
    code, out, _ = cli_runner("zzt-one")
    assert code == 2
    assert out == ""
    assert calls == []


def test_argument_count_above_maximum_is_usage_error_and_handler_not_called():
    calls = []

    def handler(args):
        calls.append(list(args))
        return [["x"]]

    register(("zzt-one-max",), handler, (1, 1))
    code, out, _ = cli_runner("zzt-one-max", "a", "b")
    assert code == 2
    assert calls == []


def test_argument_count_within_range_reaches_the_handler():
    calls = []

    def handler(args):
        calls.append(list(args))
        return [["x"]]

    register(("zzt-one-ok",), handler, (1, 1))
    code, out, _ = cli_runner("zzt-one-ok", "a")
    assert code == 0
    assert out == "x\n"
    assert calls == [["a"]]


def test_multiword_command_dispatches_on_both_words():
    register(("zzt-grp", "sub"), lambda args: [["ok"]], (0, 0))
    code, out, _ = cli_runner("zzt-grp", "sub")
    assert code == 0
    assert out == "ok\n"


def test_first_word_alone_of_a_multiword_command_is_usage_error():
    register(("zzt-grp2", "sub"), lambda args: [["ok"]], (0, 0))
    code, out, _ = cli_runner("zzt-grp2")
    assert code == 2
    assert out == ""


def test_unknown_second_word_of_a_multiword_command_is_usage_error():
    register(("zzt-grp3", "sub"), lambda args: [["ok"]], (0, 0))
    code, out, _ = cli_runner("zzt-grp3", "nosuch")
    assert code == 2
    assert out == ""


def test_longest_prefix_wins_over_a_shorter_registered_command():
    register(("zzt-pre",), lambda args: [["short"]], (0, 9))
    register(("zzt-pre", "long"), lambda args: [["long"]], (0, 0))
    assert cli_runner("zzt-pre", "long")[1] == "long\n"
    assert cli_runner("zzt-pre", "other")[1] == "short\n"


def test_duplicate_registration_is_refused():
    register(("zzt-dup",), lambda args: None, (0, 0))
    with pytest.raises(ValueError):
        register(("zzt-dup",), lambda args: None, (0, 0))


def test_empty_word_tuple_is_refused():
    with pytest.raises(ValueError):
        register((), lambda args: None, (0, 0))


def test_inverted_argument_range_is_refused():
    with pytest.raises(ValueError):
        register(("zzt-range",), lambda args: None, (2, 1))


def test_open_store_returns_a_database_and_creates_the_sqlite_parent_directory(tmp_path, monkeypatch):
    target = tmp_path / "nested" / "dir" / "ledger.db"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(target))
    db = open_store()
    assert isinstance(db, Database)
    assert target.parent.is_dir()


def test_open_store_accepts_a_sqlite_url_prefix(tmp_path, monkeypatch):
    target = tmp_path / "prefixed" / "ledger.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite://{target}")
    db = open_store()
    assert isinstance(db, Database)
    assert Path(target).parent.is_dir()
