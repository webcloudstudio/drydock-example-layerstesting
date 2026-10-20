"""Foundation checks: project manifest, lock file, environment, and launchers.

Each test acts on the project and reads the resulting state back. None of them
inspect captured text beyond parsed JSON or an exit status.
"""

import json
import os
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def _load_pyproject() -> dict:
    with open(ROOT / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)


def _requirement_names(specs: list[str]) -> set[str]:
    names = set()
    for spec in specs:
        name = spec
        for sep in ("<", ">", "=", "!", "~", "[", ";", " "):
            name = name.split(sep, 1)[0]
        names.add(name.strip().lower())
    return names


# --- pyproject.toml -------------------------------------------------------------------


def test_pyproject_parses_with_project_table():
    data = _load_pyproject()
    assert isinstance(data["project"], dict)


def test_pyproject_names_the_ledger_project():
    assert _load_pyproject()["project"]["name"] == "ledger"


def test_pyproject_requires_python_311_or_newer():
    spec = _load_pyproject()["project"]["requires-python"]
    assert spec == ">=3.11"


def test_pyproject_declares_pytest_and_ruff_as_dev_dependencies():
    dev = _load_pyproject()["dependency-groups"]["dev"]
    assert {"pytest", "ruff"} <= _requirement_names(dev)


def test_pyproject_points_pytest_at_tests_directory():
    assert _load_pyproject()["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


# --- uv.lock --------------------------------------------------------------------------


def test_uv_lock_is_committed_beside_pyproject():
    assert (ROOT / "uv.lock").is_file()


def test_uv_lock_pins_pytest_and_ruff():
    with open(ROOT / "uv.lock", "rb") as handle:
        lock = tomllib.load(handle)
    pinned = {package["name"] for package in lock["package"]}
    assert {"pytest", "ruff"} <= pinned


# --- .venv ----------------------------------------------------------------------------


def test_venv_interpreter_runs_and_reports_python_311_or_newer():
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", "import sys, json; print(json.dumps(list(sys.version_info[:2])))"],
        capture_output=True,
        text=True,
        check=True,
    )
    major, minor = json.loads(result.stdout)
    assert (major, minor) >= (3, 11)


def test_venv_provides_pytest_and_ruff_executables():
    for tool in ("pytest", "ruff"):
        assert os.access(ROOT / ".venv" / "bin" / tool, os.X_OK)


# --- bin/ launchers -------------------------------------------------------------------


@pytest.mark.parametrize("launcher", ["bin/test.sh", "bin/lint.sh"])
def test_launcher_is_an_executable_file(launcher):
    path = ROOT / launcher
    assert path.is_file()
    assert os.access(path, os.X_OK)


@pytest.mark.parametrize("launcher", ["bin/test.sh", "bin/lint.sh"])
def test_launcher_declares_commandcenter_header(launcher):
    lines = (ROOT / launcher).read_text().splitlines()
    assert lines[0] == "#!/bin/sh"
    assert lines[1] == "# CommandCenter Operation"


def test_lint_launcher_exits_zero_on_clean_project():
    result = subprocess.run(["sh", str(ROOT / "bin" / "lint.sh")], check=False, cwd=ROOT)
    assert result.returncode == 0


# --- .gitignore -----------------------------------------------------------------------


def test_gitignore_excludes_venv_and_runtime_data():
    entries = {line.strip() for line in (ROOT / ".gitignore").read_text().splitlines()}
    assert {".venv/", "data/", ".env"} <= entries
