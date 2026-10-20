from __future__ import annotations

from cli.testing import cli_runner


def test_help_is_available_for_command_families() -> None:
    for args in (("--help",), ("account", "--help"), ("txn", "--help"), ("report", "--help")):
        code, _stdout, _stderr = cli_runner(*args)
        assert code == 0


def test_unknown_root_command_returns_usage_failure() -> None:
    code, stdout, _stderr = cli_runner("frobnicate")
    assert code == 2
    assert stdout == ""


def test_unknown_report_returns_usage_failure() -> None:
    code, stdout, _stderr = cli_runner("report", "nosuch")
    assert code == 2
    assert stdout == ""


def test_command_families_require_their_arguments() -> None:
    for args in (("account",), ("txn",), ("load",), ("transfer",), ("report",)):
        code, stdout, _stderr = cli_runner(*args)
        assert code == 2
        assert stdout == ""


def test_declared_command_can_be_dispatched() -> None:
    code, stdout, stderr = cli_runner("init")
    assert code == 0
    assert stdout == ""
    assert stderr == ""
