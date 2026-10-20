import os
from pathlib import Path

from cli.testing import cli_runner


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_runner_is_executable():
    runner = PROJECT_ROOT / "bin" / "test.sh"

    assert runner.is_file()
    assert os.access(runner, os.X_OK)


def test_project_suite_smoke_covers_the_public_report_surface(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "ledger.db"))
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    assert cli_runner("init")[0] == 0
    assert cli_runner("count")[0] == 0
    assert cli_runner("report", "balances")[0] == 0
    assert cli_runner("report", "categories")[0] == 0
    assert cli_runner("report", "monthly")[0] == 0
