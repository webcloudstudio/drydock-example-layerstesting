"""In-process test entry: runs a command and returns what it wrote, without spawning a process."""

import contextlib
import io

from cli import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    """Return (exit_code, stdout, stderr) for one command run in this process."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()
