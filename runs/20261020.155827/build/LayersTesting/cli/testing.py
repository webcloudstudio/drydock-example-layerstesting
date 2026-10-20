"""In-process runner for deterministic CLI acceptance tests."""
from __future__ import annotations

import contextlib
import io

from cli import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    """Return ``(exit_code, stdout, stderr)`` without spawning a process."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(list(args))
    return code, stdout.getvalue(), stderr.getvalue()
