# FEATURE: Exit Codes

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Each command returns one of exit codes 0 to 4, and a failing command writes one diagnostic line to standard error and nothing to standard output. |
| Depends On  | FEATURE-CSV-OUTPUT.md, FEATURE-AMOUNT-CENTS.md |
| Provides    | cli.errors.LedgerError(code, message), cli.errors.run_command(handler) -> int |

## Purpose

The exit code is the contract a caller reads. This story gives every command one place to convert
its outcome into an exit code and a diagnostic.

## Behavior

- `LedgerError(code, message)` carries an exit code in `code` and a single-line message. Its code
  is one of 1, 2, 3, or 4.
- `run_command(handler)` calls `handler()`. The handler returns the CSV text to print.
  - On success, `run_command` writes the returned text to standard output and returns `0`.
  - On `LedgerError`, `run_command` writes one line to standard error and returns `error.code`,
    writing nothing to standard output.
- Exit codes follow the Exit codes table: 1 operational, 2 usage, 3 rejected, 4 not found.

## Programmatic Acceptance

=== AC exit-success-writes-output-and-zero ===
Intent: run_command returns 0 and writes exactly the handler's returned text to standard output on success.

import contextlib
import io

from cli.errors import run_command

body = "account,name\nDRAWER1,Front Drawer\n"
out = io.StringIO()
err = io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    code = run_command(lambda: body)
assert code == 0
assert out.getvalue() == body
assert err.getvalue() == ""
=== END AC exit-success-writes-output-and-zero ===

=== AC exit-failure-codes-mapped ===
Intent: For each failure code 1 to 4, run_command returns that code, writes nothing to standard output, and writes exactly one line to standard error.

import contextlib
import io

from cli.errors import LedgerError, run_command

def failing(code):
    def handler():
        raise LedgerError(code, "rejected input")
    return handler

for code in [1, 2, 3, 4]:
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = run_command(failing(code))
    assert result == code
    assert out.getvalue() == ""
    assert err.getvalue().count("\n") == 1
=== END AC exit-failure-codes-mapped ===

=== AC exit-error-carries-code ===
Intent: LedgerError exposes the exit code it was constructed with.

from cli.errors import LedgerError

error = LedgerError(3, "rejected input")
assert error.code == 3
=== END AC exit-error-carries-code ===

## User Acceptance

- None.

## Guardrails

- Only the codes 0, 1, 2, 3, and 4 are produced by this mechanism.
- A failing command never writes to standard output, including output it had begun to compute.
- Standard error is not compared by acceptance. It carries one diagnostic line on failure.
