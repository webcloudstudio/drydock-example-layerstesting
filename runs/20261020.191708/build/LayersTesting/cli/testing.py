"""Test boundary for invoking the CLI in-process."""

from __future__ import annotations

import io
from collections.abc import Iterator
from contextlib import redirect_stderr, redirect_stdout

from . import main


def cli_runner(*argv: str) -> tuple[int, str, str]:
    """Run a CLI command and return its exit status and captured streams."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()
