"""In-process test fixture for the ``cli`` package. Runs ``main`` without spawning a process."""

from __future__ import annotations

import contextlib
import io

from cli import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    """Return ``(exit_code, stdout, stderr)`` for ``ledger`` invoked with ``args``."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()
