# FEATURE: CLI Entry

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The `ledger` executable, the `cli` dispatcher and the exit-code error mapping. |
| Depends On | ARCHITECTURE.md, DATABASE.md |
| Provides | ledger, cli.main |
| Consumes | python-project, persistence |

## Purpose

Give every command one entry point with one failure contract: output is buffered and written only on
success, and any failure produces one line on standard error, nothing on standard output, and a
conventional exit code.

## Interface

- `ledger` at the application root is an executable POSIX sh launcher. It runs
  `cli.main(sys.argv[1:])` with `.venv/bin/python` when present, otherwise `python3`, and exits with
  the returned value.
- `cli.main(argv: list[str] | None = None) -> int`.
- `cli/testing.py` provides `cli_runner(*args) -> (exit_code, stdout, stderr)`.
- `cli/errors.py` defines `CliError` with an `exit_code` attribute and the subclasses
  `OperationalError` (1), `UsageError` (2), `RejectedError` (3) and `NotFoundError` (4).
- `cli/commands/` is a package. `argv[0]` names the module `cli.commands.<command>`, imported
  lazily; each module exposes `run(args: list[str]) -> list[str]` returning output lines and
  printing nothing.

## Behavior

- With no arguments, or when the command module does not exist, `main` raises a usage error:
  exit 2, nothing on standard output, one diagnostic line on standard error.
- On success `main` writes the returned lines to standard output, each ended by `\n`, and returns 0.
- A `CliError` raised by a command produces one diagnostic line on standard error, nothing on
  standard output, and the error's `exit_code`.
- Any other exception is an operational failure: exit 1, one diagnostic line, nothing on standard
  output.
- The remaining arguments after the command name are passed to `run` unchanged.
- No command logic lives in this feature.

## Database Interface

- None — persistence is declared by DATABASE.md and reached through ledgerlib by later features.

## Programmatic Acceptance

=== AC cli-no-arguments ===
Intent: Calling main with no arguments is a usage error with exit 2 and an empty standard output.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(out)
print(err)
assert code == 2
assert out == ""
=== END AC cli-no-arguments ===

=== AC cli-unknown-command ===
Intent: An unknown command exits 2, writes nothing to standard output and one diagnostic line to standard error.

from cli.testing import cli_runner

code, out, err = cli_runner("zzunknowncommand")
print(out)
print(err)
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC cli-unknown-command ===

=== AC cli-error-mapping ===
Intent: Each CliError subclass maps to its exit code, with empty standard output and one standard error line.

import sys
import types

from cli.errors import NotFoundError, OperationalError, RejectedError, UsageError
from cli.testing import cli_runner

expected = {OperationalError: 1, UsageError: 2, RejectedError: 3, NotFoundError: 4}
for error_class, status in expected.items():
    def run(args, error_class=error_class):
        raise error_class("probe failure")

    module = types.ModuleType("cli.commands.zzprobe")
    module.run = run
    sys.modules["cli.commands.zzprobe"] = module
    code, out, err = cli_runner("zzprobe")
    print(code, repr(out), repr(err))
    assert code == status
    assert error_class("x").exit_code == status
    assert out == ""
    assert len(err.strip().splitlines()) == 1
sys.modules.pop("cli.commands.zzprobe", None)
=== END AC cli-error-mapping ===

=== AC cli-unexpected-exception ===
Intent: An unexpected exception from a command is an operational failure with exit 1 and empty standard output.

import sys
import types

from cli.testing import cli_runner

def run(args):
    raise RuntimeError("probe crash")

module = types.ModuleType("cli.commands.zzcrash")
module.run = run
sys.modules["cli.commands.zzcrash"] = module
code, out, err = cli_runner("zzcrash")
sys.modules.pop("cli.commands.zzcrash", None)
print(code, repr(out), repr(err))
assert code == 1
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC cli-unexpected-exception ===

=== AC cli-success-output ===
Intent: A successful command's lines reach standard output one per line with newline endings, and arguments pass through unchanged.

import sys
import types

from cli.testing import cli_runner

lines = ["header,value", "alpha,beta"]
passed_args = ["first", "second"]
received = []

def run(args):
    received.append(list(args))
    return lines

module = types.ModuleType("cli.commands.zzok")
module.run = run
sys.modules["cli.commands.zzok"] = module
code, out, err = cli_runner("zzok", *passed_args)
sys.modules.pop("cli.commands.zzok", None)
print(code, repr(out), repr(err))
assert code == 0
assert out.splitlines() == lines
assert out.endswith("\n")
assert "\r" not in out
assert received == [passed_args]
=== END AC cli-success-output ===

=== AC cli-executable-launcher ===
Intent: The ledger executable exists at the application root and exits 2 for an unknown command without touching a database.

import os
import subprocess

path = "./ledger"
assert os.path.isfile(path)
assert os.access(path, os.X_OK)
result = subprocess.run([path, "zzunknowncommand"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC cli-executable-launcher ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to standard output.
- Diagnostics go to standard error and are never compared.
- This feature contains no command logic and opens no database driver.
