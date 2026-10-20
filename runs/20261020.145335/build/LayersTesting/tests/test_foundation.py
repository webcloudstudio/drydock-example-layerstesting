"""Foundation contract: project manifest, lock file, environment, and launchers."""

import os
import stat
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def manifest() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _lock_package_names() -> set[str]:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    return {package["name"] for package in lock["package"]}


def test_requires_python_3_11_or_newer(manifest: dict) -> None:
    requires = manifest["project"]["requires-python"]
    assert isinstance(requires, str)
    assert "3.11" in requires


def test_runtime_dependencies_include_psycopg(manifest: dict) -> None:
    dependencies = manifest["project"]["dependencies"]
    assert any(item.startswith("psycopg") for item in dependencies)


def test_dev_group_includes_pytest(manifest: dict) -> None:
    dev_group = manifest["dependency-groups"]["dev"]
    assert any(item.startswith("pytest") for item in dev_group)


def test_lock_file_resolves_psycopg_and_pytest() -> None:
    names = _lock_package_names()
    assert "psycopg" in names
    assert "psycopg-binary" in names
    assert "pytest" in names


def test_venv_directory_exists() -> None:
    assert (ROOT / ".venv").is_dir()


def test_venv_interpreter_meets_minimum_version() -> None:
    config = (ROOT / ".venv" / "pyvenv.cfg").read_text(encoding="utf-8")
    version_line = next(
        line for line in config.splitlines() if line.startswith("version_info")
    )
    major, minor = (int(part) for part in version_line.split("=", 1)[1].split(".")[:2])
    assert (major, minor) >= (3, 11)


@pytest.mark.parametrize("launcher", ["bin/test.sh", "bin/sync.sh"])
def test_launcher_is_executable_posix_script(launcher: str) -> None:
    path = ROOT / launcher
    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("#!/bin/sh\n")
    if os.name == "posix":
        assert path.stat().st_mode & stat.S_IXUSR
