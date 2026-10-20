"""Command dispatch: help for every command, and usage errors that exit 2 with one stderr line."""

import pytest

from cli.testing import cli_runner

COMMANDS_WITH_HELP = [
    ["init"],
    ["count"],
    ["load"],
    ["account", "add"],
    ["account", "get"],
    ["account", "rename"],
    ["account", "delete"],
    ["txn", "post"],
    ["txn", "get"],
    ["txn", "amend"],
    ["txn", "delete"],
    ["transfer"],
    ["report", "balances"],
    ["report", "categories"],
    ["report", "monthly"],
]

USAGE_ERRORS = [
    ["frobnicate"],
    ["load", "nosuch", "bogus.csv"],
    ["load", "accounts"],
    ["report", "nosuch"],
    ["report"],
    ["account"],
    ["txn", "get"],
    ["txn", "get", "not-a-number"],
    ["init", "extra"],
]


def _non_blank_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def test_top_level_help_exits_zero_with_usage_on_stdout() -> None:
    code, out, err = cli_runner("--help")
    assert code == 0
    assert out.strip() != ""
    assert err == ""


@pytest.mark.parametrize("words", COMMANDS_WITH_HELP, ids=" ".join)
def test_command_help_exits_zero_with_usage_on_stdout(words: list[str]) -> None:
    code, out, err = cli_runner(*words, "--help")
    assert code == 0
    assert out.strip() != ""
    assert err == ""


@pytest.mark.parametrize("group", ["account", "txn", "report"])
def test_group_help_exits_zero_with_usage_on_stdout(group: str) -> None:
    code, out, err = cli_runner(group, "--help")
    assert code == 0
    assert out.strip() != ""
    assert err == ""


@pytest.mark.parametrize("argv", USAGE_ERRORS, ids=" ".join)
def test_usage_error_exits_two_with_empty_stdout(argv: list[str]) -> None:
    code, out, _ = cli_runner(*argv)
    assert code == 2
    assert out == ""


@pytest.mark.parametrize("argv", USAGE_ERRORS, ids=" ".join)
def test_usage_error_writes_exactly_one_stderr_line(argv: list[str]) -> None:
    _, _, err = cli_runner(*argv)
    assert len(_non_blank_lines(err)) == 1


def test_no_arguments_exits_two_with_one_usage_line() -> None:
    code, out, err = cli_runner()
    assert code == 2
    assert out == ""
    assert len(_non_blank_lines(err)) == 1


def test_txn_get_accepts_one_numeric_transaction_number() -> None:
    # Parsing succeeds and reaches dispatch; no handler is built yet, so the command is not run.
    code, out, _ = cli_runner("txn", "get", "7")
    assert code != 2
    assert out == ""


def test_recognized_command_without_handler_exits_one_not_two() -> None:
    code, out, _ = cli_runner("count")
    assert code == 1
    assert out == ""
