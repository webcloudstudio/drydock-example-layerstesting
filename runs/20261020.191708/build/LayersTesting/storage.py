"""Typed application file boundary."""

from __future__ import annotations

from pathlib import Path


class FileStore:
    """Read generated application assets relative to a known application file."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve()

    def read(self, name: str) -> str:
        return (self._root / name).read_text(encoding="utf-8")
