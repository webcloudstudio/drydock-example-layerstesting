"""Project foundation: files, importable packages, and the static rules on domain code."""

import ast
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOMAIN_ROOT = ROOT / "ledger_core"
BANNED_DRIVERS = {"sqlite3", "psycopg", "psycopg2"}


@pytest.mark.parametrize("name", ["pyproject.toml", "uv.lock", "conftest.py", "bin/test.sh"])
def test_project_file_exists(name):
    assert (ROOT / name).is_file()


def test_test_launcher_runs_pytest():
    assert "pytest" in (ROOT / "bin" / "test.sh").read_text()


@pytest.mark.parametrize("module", ["ledger_core", "ledger_core.config", "ledger_core.errors"])
def test_foundation_module_imports(module):
    assert importlib.import_module(module) is not None


def _domain_files():
    return sorted(DOMAIN_ROOT.rglob("*.py"))


def test_domain_files_are_scanned():
    assert len(_domain_files()) >= 1


def _imported_top_level_names(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or "").split(".")[0]


@pytest.mark.parametrize("path", _domain_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_domain_module_imports_no_database_driver(path):
    tree = ast.parse(path.read_text())
    assert not (BANNED_DRIVERS & set(_imported_top_level_names(tree)))


@pytest.mark.parametrize("path", _domain_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_domain_module_has_no_float_call_or_literal(path):
    tree = ast.parse(path.read_text())
    float_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "float"
    ]
    float_literals = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert not float_calls
    assert not float_literals
