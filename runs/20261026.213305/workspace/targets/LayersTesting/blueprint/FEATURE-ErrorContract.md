# FEATURE: Error Contract

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Error types, exit codes and the one-line standard error diagnostic for failed commands. |
| Depends On | FEATURE-CliFoundation.md |
| Provides | ledger_errors.Rejected, ledger_errors.NotFound, ledger_errors.OperationalFailure, ledger_errors.UsageError |
| Consumes | ledger.register_command |

## Purpose

Failures map to a fixed exit code and exactly one diagnostic line on standard error; standard output stays empty.

## Interface

- `ledger_errors.LedgerError(Exception)` is the base, with class attribute `exit_code`.
- `Rejected` has `exit_code` 3, `NotFound` 4, `OperationalFailure` 1, `UsageError` 2.
- `ledger_errors.handle(exc: BaseException) -> int` writes one line to standard error and returns the exit code: the `exit_code` of a `LedgerError`, otherwise `1` (unexpected errors, including database errors). The message has newlines collapsed to spaces and every `scheme://...` token replaced by `<redacted>`, so a DSN or password never reaches a diagnostic.
- `cli.main` calls `handle` for any exception raised by a handler. An unknown command or empty argument list is a `UsageError` and exits 2.

## Programmatic Acceptance

=== AC errors-exit-codes ===
Intent: Each error type carries the exit code from the contract and derives from the common base.

import ledger_errors

assert ledger_errors.OperationalFailure.exit_code == 1
assert ledger_errors.UsageError.exit_code == 2
assert ledger_errors.Rejected.exit_code == 3
assert ledger_errors.NotFound.exit_code == 4
for cls in (
    ledger_errors.OperationalFailure,
    ledger_errors.UsageError,
    ledger_errors.Rejected,
    ledger_errors.NotFound,
):
    assert issubclass(cls, ledger_errors.LedgerError)
=== END AC errors-exit-codes ===

=== AC errors-through-main ===
Intent: A handler raising each error type makes main return its exit code with empty standard output and one stderr line.

import cli
import ledger_errors
from cli.testing import cli_runner

cases = {
    "zzrej": (ledger_errors.Rejected, 3),
    "zznf": (ledger_errors.NotFound, 4),
    "zzop": (ledger_errors.OperationalFailure, 1),
    "zzuse": (ledger_errors.UsageError, 2),
}
for name, (cls, expected_code) in cases.items():
    def handler(args, cls=cls):
        raise cls("diagnostic text")
    cli.register_command(name, handler)
    code, out, err = cli_runner(name)
    assert code == expected_code
    assert out == ""
    assert len(err.splitlines()) == 1
=== END AC errors-through-main ===

=== AC errors-unexpected-exception ===
Intent: An unexpected exception from a handler exits 1 with empty standard output.

import cli
from cli.testing import cli_runner

name = "zzboom"
def handler(args):
    raise RuntimeError("unexpected")
cli.register_command(name, handler)
code, out, err = cli_runner(name)
assert code == 1
assert out == ""
assert len(err.splitlines()) == 1
=== END AC errors-unexpected-exception ===

=== AC errors-unknown-command-usage ===
Intent: An unknown command is a usage error: exit 2, empty standard output, one diagnostic line.

from cli.testing import cli_runner

code, out, err = cli_runner("zzdoesnotexist")
assert code == 2
assert out == ""
assert len(err.splitlines()) == 1
=== END AC errors-unknown-command-usage ===

=== AC errors-multiline-message-single-line ===
Intent: A multi-line error message is still written as exactly one diagnostic line.

import cli
import ledger_errors
from cli.testing import cli_runner

name = "zzmulti"
message = "first line\nsecond line"
def handler(args):
    raise ledger_errors.Rejected(message)
cli.register_command(name, handler)
code, out, err = cli_runner(name)
assert code == 3
assert len(err.splitlines()) == 1
=== END AC errors-multiline-message-single-line ===

=== AC errors-dsn-never-echoed ===
Intent: A password inside a DSN in an error message never appears on standard error or standard output.

import cli
import ledger_errors
from cli.testing import cli_runner

name = "zzsecret"
password = "s3cretpw"
message = "cannot open postgres://user:" + password + "@host/db"
def handler(args):
    raise ledger_errors.OperationalFailure(message)
cli.register_command(name, handler)
code, out, err = cli_runner(name)
assert code == 1
assert password not in err
assert password not in out
=== END AC errors-dsn-never-echoed ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to standard output.
- A diagnostic never contains a database URL, path credential or DSN password.
- Diagnostic text is never part of the contract; only the exit code is.
