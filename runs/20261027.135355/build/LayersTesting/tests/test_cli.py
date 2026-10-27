"""CLI entry: registry loading, dispatch, usage errors, domain exit codes, and the stdout contract."""

import csv
import io
import os
import subprocess
from pathlib import Path

import pytest

from cli import registry
from cli.testing import cli_runner
from ledger_core.errors import NotFound, Operational, Rejected

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def scratch_commands():
    """Register probe commands for one test and remove exactly those afterwards."""
    registry.load()
    before = dict(registry.COMMANDS)
    yield registry.COMMANDS
    registry.COMMANDS.clear()
    registry.COMMANDS.update(before)


def test_load_is_idempotent():
    registry.load()
    first = dict(registry.COMMANDS)
    registry.load()
    assert registry.COMMANDS == first


def test_registry_keys_are_word_tuples():
    registry.load()
    for words in registry.COMMANDS:
        assert isinstance(words, tuple)
        assert all(isinstance(word, str) for word in words)


def test_load_keeps_entries_added_by_hand(scratch_commands):
    key = ("zztest", "kept")
    scratch_commands[key] = registry.Command(lambda db, args: [], 0, 0)
    registry.load()
    assert key in registry.COMMANDS


def test_unknown_command_exits_two_with_one_stderr_line():
    code, out, err = cli_runner("zzfrobnicate")
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_no_command_exits_two_with_one_stderr_line():
    code, out, err = cli_runner()
    assert code == 2
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_group_word_alone_is_usage_error(scratch_commands):
    scratch_commands[("zzgrp", "ok")] = registry.Command(lambda db, args: [["h"]], 0, 0)
    code, out, _ = cli_runner("zzgrp")
    assert code == 2
    assert out == ""


def test_group_word_with_unknown_sub_word_is_usage_error(scratch_commands):
    scratch_commands[("zzgrp", "ok")] = registry.Command(lambda db, args: [["h"]], 0, 0)
    code, out, _ = cli_runner("zzgrp", "nosuch")
    assert code == 2
    assert out == ""


@pytest.mark.parametrize("extra", [(), ("a", "b")])
def test_wrong_argument_count_is_usage_error(scratch_commands, extra):
    scratch_commands[("zzcount", "ok")] = registry.Command(lambda db, args: [["h"]], 1, 1)
    code, out, err = cli_runner("zzcount", "ok", *extra)
    assert code == 2
    assert out == ""
    assert err.strip() != ""


def test_unbounded_max_args_accepts_many(scratch_commands):
    scratch_commands[("zzmany",)] = registry.Command(lambda db, args: [[str(len(args))]], 0, None)
    code, out, _ = cli_runner("zzmany", "a", "b", "c", "d")
    assert code == 0
    assert out == "4\n"


def test_handler_receives_arguments_after_command_words(scratch_commands):
    seen = {}

    def handler(db, args):
        seen["db"] = db
        seen["args"] = args
        return [["x"]]

    scratch_commands[("zzargs", "go")] = registry.Command(handler, 2, 2)
    code, _, _ = cli_runner("zzargs", "go", "one", "two")
    assert code == 0
    assert seen["args"] == ["one", "two"]
    assert seen["db"] is not None


def test_rows_print_as_unquoted_csv_with_newline_endings(scratch_commands):
    scratch_commands[("zzcsv", "ok")] = registry.Command(
        lambda db, args: [["h1", "h2"], [args[0], "v"]], 1, 1
    )
    code, out, _ = cli_runner("zzcsv", "ok", "alpha")
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["h1", "h2"], ["alpha", "v"]]
    assert "\r" not in out
    assert out == "h1,h2\nalpha,v\n"


def test_no_rows_prints_nothing(scratch_commands):
    scratch_commands[("zzempty", "ok")] = registry.Command(lambda db, args: [], 0, 0)
    code, out, err = cli_runner("zzempty", "ok")
    assert code == 0
    assert out == ""
    assert err == ""


def test_no_trailing_spaces_in_output(scratch_commands):
    scratch_commands[("zzpad", "ok")] = registry.Command(lambda db, args: [["a", "b"]], 0, 0)
    _, out, _ = cli_runner("zzpad", "ok")
    assert all(not line.endswith(" ") for line in out.splitlines())


@pytest.mark.parametrize(
    ("error", "expected"),
    [(Rejected, 3), (NotFound, 4), (Operational, 1)],
)
def test_domain_error_maps_to_exit_code(scratch_commands, error, expected):
    def handler(db, args):
        raise error("probe failure")

    scratch_commands[("zzerr", "probe")] = registry.Command(handler, 0, 0)
    code, out, err = cli_runner("zzerr", "probe")
    assert code == expected
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_unexpected_exception_exits_one_with_empty_stdout(scratch_commands):
    def handler(db, args):
        raise RuntimeError("boom")

    scratch_commands[("zzboom", "probe")] = registry.Command(handler, 0, 0)
    code, out, err = cli_runner("zzboom", "probe")
    assert code == 1
    assert out == ""
    assert len(err.strip().splitlines()) == 1


def test_stdout_is_empty_when_handler_fails_after_partial_work(scratch_commands):
    def handler(db, args):
        raise Rejected("late rule")

    scratch_commands[("zzlate", "probe")] = registry.Command(handler, 0, 0)
    code, out, _ = cli_runner("zzlate", "probe")
    assert code == 3
    assert out == ""


def test_unopenable_database_exits_one_with_empty_stdout(scratch_commands, monkeypatch, tmp_path):
    absent = tmp_path / "absent"
    monkeypatch.setenv("DATABASE_URL", str(absent / "app.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    scratch_commands[("zzopen", "ok")] = registry.Command(lambda db, args: [["h"]], 0, 0)
    code, out, _ = cli_runner("zzopen", "ok")
    assert code == 1
    assert out == ""
    assert not absent.exists()


def test_main_returns_rather_than_exits(scratch_commands):
    scratch_commands[("zzret", "ok")] = registry.Command(lambda db, args: [["h"]], 0, 0)
    from cli import main

    assert main(["zzret", "ok"]) == 0


def test_ledger_launcher_is_executable():
    assert os.access(ROOT / "ledger", os.X_OK)


def test_ledger_launcher_returns_usage_exit_code_for_unknown_command():
    result = subprocess.run(
        [str(ROOT / "ledger"), "zzfrobnicate"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 2
    assert result.stdout == ""
