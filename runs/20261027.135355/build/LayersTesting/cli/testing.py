"""In-process command runner for tests. Runs ``main`` without spawning a process."""

import contextlib
import io

from cli import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    """Return ``(exit_code, stdout, stderr)`` without spawning a process."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()
