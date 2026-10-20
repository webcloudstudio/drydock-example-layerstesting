"""CLI entry contract: main returns a status, cli_runner returns a tuple, and the ledger launcher agrees."""

import os
import stat
import subprocess
from pathlib import Path

from cli import main
from cli.testing import cli_runner

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledger"


def test_main_returns_usage_status_for_unknown_command() -> None:
    assert main(["no-such-command"]) == 2


def test_main_returns_usage_status_without_arguments() -> None:
    assert main([]) == 2


def test_main_returns_zero_for_help() -> None:
    assert main(["--help"]) == 0


def test_cli_runner_returns_int_and_two_strings() -> None:
    code, out, err = cli_runner("no-such-command")
    assert isinstance(code, int)
    assert isinstance(out, str)
    assert isinstance(err, str)


def test_cli_runner_status_matches_main() -> None:
    code, _, _ = cli_runner("no-such-command")
    assert code == main(["no-such-command"])


def test_cli_runner_help_returns_zero() -> None:
    code, _, _ = cli_runner("--help")
    assert code == 0


def test_ledger_launcher_is_executable_file_at_root() -> None:
    assert LEDGER.is_file()
    if os.name == "posix":
        assert LEDGER.stat().st_mode & stat.S_IXUSR


def test_ledger_launcher_exit_status_matches_cli_runner() -> None:
    args = ["no-such-command"]
    code, _, _ = cli_runner(*args)
    proc = subprocess.run([str(LEDGER), *args], capture_output=True, text=True, check=False)
    assert proc.returncode == code


def test_ledger_launcher_help_exits_zero() -> None:
    proc = subprocess.run([str(LEDGER), "--help"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0
