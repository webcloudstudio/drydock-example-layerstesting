"""Scaffold contract: the project manifest, lockfile, and environment exist as declared."""

import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_manifest() -> dict:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def _dependency_names() -> set[str]:
    entries = _load_manifest()["project"]["dependencies"]
    return {re.split(r"[<>=!~\[ ;]", entry, maxsplit=1)[0].lower() for entry in entries}


def test_manifest_requires_python_311_or_newer():
    assert _load_manifest()["project"]["requires-python"].startswith(">=3.11")


def test_manifest_declares_pytest_and_psycopg():
    assert {"pytest", "psycopg"} <= _dependency_names()


def test_lockfile_is_committed_in_project_root():
    assert (PROJECT_ROOT / "uv.lock").is_file()


def test_virtual_environment_directory_exists():
    assert (PROJECT_ROOT / ".venv").is_dir()


def test_gitignore_excludes_virtual_environment():
    lines = (PROJECT_ROOT / ".gitignore").read_text().splitlines()
    assert ".venv/" in lines
