"""Foundation checks: project manifest, environment contract, and the ledger launcher file."""

import os
import stat
import tomllib
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_declares_python_requirement():
    with open(APP_ROOT / "pyproject.toml", "rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["requires-python"] == ">=3.11"


def test_pyproject_declares_pytest_in_dev_group():
    with open(APP_ROOT / "pyproject.toml", "rb") as fh:
        data = tomllib.load(fh)
    dev = data["dependency-groups"]["dev"]
    assert any(spec.startswith("pytest") for spec in dev)


def test_uv_lock_is_committed_alongside_manifest():
    assert (APP_ROOT / "uv.lock").is_file()


def test_ledger_launcher_is_a_file_at_application_root():
    assert (APP_ROOT / "ledger").is_file()


def test_ledger_launcher_is_executable():
    mode = (APP_ROOT / "ledger").stat().st_mode
    assert mode & stat.S_IXUSR
    assert os.access(APP_ROOT / "ledger", os.X_OK)


def test_ledger_launcher_starts_with_interpreter_line():
    with open(APP_ROOT / "ledger", "rb") as fh:
        assert fh.read(2) == b"#!"


def test_test_launcher_is_present():
    assert (APP_ROOT / "bin" / "test.sh").is_file()


def test_gitignore_excludes_environment_and_runtime_data():
    lines = (APP_ROOT / ".gitignore").read_text().splitlines()
    assert ".venv/" in lines
    assert "data/" in lines


def test_env_example_documents_database_settings():
    text = (APP_ROOT / ".env.example").read_text()
    assert "DATABASE_URL=" in text
    assert "DATABASE_PATH=" in text
