"""CLI platform: the main entry point, the cli_runner fixture, and the ledger launcher.

Tests call ``main`` or ``cli_runner`` in process. One subprocess test covers the launcher, and
it asserts only on the exit status.
"""

import inspect
import subprocess
import sys
from pathlib import Path

import cli
from cli import testing

ROOT = Path(__file__).resolve().parents[1]


# --- main -----------------------------------------------------------------------------


def test_main_takes_a_single_argv_parameter():
    assert list(inspect.signature(cli.main).parameters) == ["argv"]


def test_main_returns_an_integer_rather_than_exiting():
    assert isinstance(cli.main(["--help"]), int)


def test_main_help_returns_zero():
    assert cli.main(["--help"]) == 0


def test_main_without_a_command_returns_usage_code_two():
    assert cli.main([]) == 2


def test_main_with_an_unknown_command_returns_usage_code_two():
    assert cli.main(["no-such-command"]) == 2


def test_main_defaults_to_sys_argv_when_called_without_arguments(monkeypatch):
    monkeypatch.setattr("sys.argv", ["ledger", "--help"])
    assert cli.main() == 0


# --- cli_runner -----------------------------------------------------------------------


def test_cli_runner_returns_exit_code_and_both_streams():
    code, out, err = testing.cli_runner("--help")
    assert code == 0
    assert err == ""
    assert out.startswith("usage: ledger")


def test_cli_runner_routes_usage_errors_to_stderr_only():
    code, out, err = testing.cli_runner()
    assert code == 2
    assert out == ""
    assert "usage: ledger" in err


def test_cli_runner_unknown_command_reports_the_name_on_stderr():
    code, out, err = testing.cli_runner("no-such-command")
    assert code == 2
    assert out == ""
    assert "'no-such-command'" in err


def test_cli_runner_fixture_is_the_runner(cli_runner):
    assert cli_runner is testing.cli_runner


def test_cli_runner_does_not_leak_output_to_the_real_streams(capsys):
    testing.cli_runner("--help")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# --- python -m cli --------------------------------------------------------------------


def test_python_dash_m_cli_exits_with_usage_code_two():
    result = subprocess.run([sys.executable, "-m", "cli"], check=False, cwd=ROOT)
    assert result.returncode == 2


# --- ledger launcher -----------------------------------------------------------------


def test_ledger_launcher_is_an_executable_file_at_the_root():
    launcher = ROOT / "ledger"
    assert launcher.is_file()
    assert launcher.stat().st_mode & 0o111


def test_ledger_launcher_begins_with_an_interpreter_line():
    first_line = (ROOT / "ledger").read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("#!")


def test_ledger_launcher_delegates_help_to_main_with_exit_zero():
    result = subprocess.run([str(ROOT / "ledger"), "--help"], check=False, cwd=ROOT)
    assert result.returncode == 0


def test_ledger_launcher_delegates_usage_error_with_exit_two_from_any_directory(tmp_path):
    result = subprocess.run([str(ROOT / "ledger")], check=False, cwd=tmp_path)
    assert result.returncode == 2
