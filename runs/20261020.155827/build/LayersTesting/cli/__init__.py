"""Importable CLI package exposing the ledger entry point."""
from __future__ import annotations

import importlib.util
from pathlib import Path


_LEGACY_ENTRY = Path(__file__).resolve().parent.parent / "cli.py"
_SPEC = importlib.util.spec_from_file_location("_ledger_cli_entry", _LEGACY_ENTRY)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - packaging failure
    raise ImportError(f"unable to load CLI entry point from {_LEGACY_ENTRY}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

main = _MODULE.main

__all__ = ["main"]
