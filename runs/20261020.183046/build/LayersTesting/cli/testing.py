"""In-process runner used by acceptance criteria and the project's tests."""

from __future__ import annotations

import contextlib
import io

from . import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    """Return ``(exit_code, stdout, stderr)`` without spawning a process."""

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(list(args))
    return code, stdout.getvalue(), stderr.getvalue()
