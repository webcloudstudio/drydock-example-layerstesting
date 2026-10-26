"""Foundation checks: interpreter, project manifest, test launcher, and the fixture module."""

import subprocess
import sys
import tomllib
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent


def test_interpreter_is_python_311_or_newer():
    assert sys.version_info >= (3, 11)


def test_pyproject_parses_and_declares_project_table():
    data = tomllib.loads((APP_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "project" in data
    assert data["project"]["requires-python"] == ">=3.11"


def test_pyproject_declares_pytest_as_dev_dependency():
    data = tomllib.loads((APP_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev = data["dependency-groups"]["dev"]
    assert any(spec.startswith("pytest") for spec in dev)


def test_lock_file_is_committed_next_to_pyproject():
    assert (APP_ROOT / "uv.lock").is_file()


def test_test_launcher_is_valid_posix_sh():
    launcher = APP_ROOT / "bin" / "test.sh"
    assert launcher.is_file()
    result = subprocess.run(["sh", "-n", str(launcher)], capture_output=True, text=True)
    assert result.returncode == 0


def test_conftest_exposes_db_session_and_cli_runner_fixtures():
    import importlib.util

    spec = importlib.util.spec_from_file_location("conftest", APP_ROOT / "tests" / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("db_session", "cli_runner"):
        assert hasattr(module, name)
