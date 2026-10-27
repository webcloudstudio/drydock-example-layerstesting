# FEATURE: Ledger CLI Foundation

| Field       | Value |
|-------------|-------|
| Version     | 20261027 V1 |
| Description | The ledger executable, the cli package entry point, command dispatch, CSV output, money handling, and exit-code mapping. |
| Depends On  | ARCHITECTURE.md, FEATURE-DatabaseSelection.md |
| Provides    | ledger, cli.main |
| Consumes    | config.open_store |

## Purpose

Provide the shared command machinery every later command story registers into.

## Interface

- `ledger` at the application root: a POSIX sh launcher that runs `cli.main` with the `.venv` interpreter when present, else `python3`, and exits with the returned code.
- `cli.main(argv: list[str] | None = None) -> int`. `None` means `sys.argv[1:]`.
- `cli.testing.cli_runner(*args) -> (exit_code, stdout, stderr)` per the CLI Foundation Contract. `main` resolves `sys.stdout` and `sys.stderr` at call time so redirection works.
- `cli.registry.register(path: tuple[str, ...], handler, needs_store: bool = True)`; a handler is `handler(args: list[str], db) -> list[list[str]] | None`. Modules in `cli/commands/` are imported automatically, so adding a module registers its commands.
- `cli.output`: renders rows as CSV: comma-separated, no quoting, `\n` line endings.
- `ledgerapp.errors`: `LedgerError` with an `exit_code`; `StoreUnavailable` (1), `FileUnreadable` (1), `UsageError` (2), `Rejected` (3), `NotFound` (4).
- `ledgerapp.money`: `parse_amount(text) -> int` converts `-?DIGITS[.D[D]]` with at most two decimals, never zero, to integer cents using integer arithmetic and raises `Rejected` otherwise; `format_cents(cents: int) -> str` writes exactly two decimals, a leading `-` when negative, and no thousands separator.

## Dispatch

1. Resolve the command by the longest registered prefix of the arguments. No arguments, an unknown command, or a known group with a missing or unknown subcommand raises `UsageError` before the store is opened.
2. When `needs_store`, open the store with `config.open_store()`; failure exits 1.
3. Call the handler with the remaining arguments. Output is written only after the handler returns, so a failing command writes nothing to standard output.
4. A `LedgerError` writes one diagnostic line naming the problem to standard error and returns its exit code. Any other exception writes one line to standard error and returns 1.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC cli-main-returns-int ===
Intent: cli.main is callable with an argument list and returns an integer exit code; an unknown command is a usage error with empty standard output.

import cli
from cli.testing import cli_runner

assert callable(cli.main)
code, out, err = cli_runner("zzfrobnicate")
print(out)
print(err)
assert isinstance(code, int)
assert code == 2
assert out == ""
=== END AC cli-main-returns-int ===

=== AC cli-no-arguments-usage ===
Intent: Calling the CLI with no arguments is a usage error that writes one diagnostic line to standard error and nothing to standard output.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(out)
print(err)
assert code == 2
assert out == ""
assert len(err.splitlines()) == 1
=== END AC cli-no-arguments-usage ===

=== AC cli-exit-code-mapping ===
Intent: Success returns 0 and writes the rows as CSV; each error class maps to its exit code with empty standard output and one diagnostic line.

from cli import registry
from cli.testing import cli_runner
from ledgerapp import errors

rows = [["alpha", "beta"], ["gamma", "delta"]]
expected_out = "".join(",".join(row) + "\n" for row in rows)


def ok(args, db):
    return rows


def make_raiser(exc_type):
    def handler(args, db):
        raise exc_type("probe diagnostic")
    return handler


registry.register(("zzprobe", "ok"), ok, needs_store=False)
cases = [
    ("rejected", errors.Rejected, 3),
    ("notfound", errors.NotFound, 4),
    ("usage", errors.UsageError, 2),
    ("unreadable", errors.FileUnreadable, 1),
    ("unavailable", errors.StoreUnavailable, 1),
]
for name, exc_type, want_code in cases:
    registry.register(("zzprobe", name), make_raiser(exc_type), needs_store=False)

code, out, err = cli_runner("zzprobe", "ok")
print(out)
print(err)
assert code == 0
assert out == expected_out

for name, exc_type, want_code in cases:
    code, out, err = cli_runner("zzprobe", name)
    print(name, code, out, err)
    assert code == want_code
    assert out == ""
    assert len(err.splitlines()) == 1
=== END AC cli-exit-code-mapping ===

=== AC cli-group-needs-subcommand ===
Intent: A known command group with a missing or unknown subcommand is a usage error, and a handler is not run.

from cli import registry
from cli.testing import cli_runner

calls = []


def handler(args, db):
    calls.append(list(args))
    return [["x"]]


registry.register(("zzgroup", "run"), handler, needs_store=False)

code, out, err = cli_runner("zzgroup")
assert code == 2
assert out == ""
code, out, err = cli_runner("zzgroup", "zzmissing")
assert code == 2
assert out == ""
assert calls == []
code, out, err = cli_runner("zzgroup", "run", "arg1")
assert code == 0
assert calls == [["arg1"]]
=== END AC cli-group-needs-subcommand ===

=== AC cli-executable-launcher ===
Intent: The ledger launcher at the application root is executable and exits 2 with empty standard output for an unknown command.

import os
import subprocess

assert os.path.isfile("ledger"), "foundation not built: ledger missing"
assert os.access("ledger", os.X_OK)
result = subprocess.run(["./ledger", "zzfrobnicate"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC cli-executable-launcher ===

=== AC cli-money-format ===
Intent: format_cents writes exactly two decimals, a leading minus for negatives, and no thousands separator; expectations are derived from the integer input with Decimal.

from decimal import Decimal

from ledgerapp import money

for cents in [-1250, 0, 500000, 5, -5, 123456789]:
    expected = Decimal(cents) / Decimal(100)
    assert money.format_cents(cents) == f"{expected:.2f}"
=== END AC cli-money-format ===

=== AC cli-money-parse-valid ===
Intent: parse_amount converts valid decimal text to integer cents; expected cents are derived from the input text with Decimal.

from decimal import Decimal

from ledgerapp import money

for text in ["45.50", "-12.5", "7", "-0.01", "5000.00", "0.1"]:
    expected = int(Decimal(text) * 100)
    result = money.parse_amount(text)
    assert isinstance(result, int)
    assert result == expected
=== END AC cli-money-parse-valid ===

=== AC cli-money-parse-invalid ===
Intent: parse_amount rejects zero, more than two decimals, and text outside the amount syntax by raising Rejected.

from ledgerapp import money
from ledgerapp.errors import Rejected

for text in ["1.234", "0", "0.00", "-0", "abc", "", "1.", ".5", "+5", "1,5"]:
    raised = False
    try:
        money.parse_amount(text)
    except Rejected:
        raised = True
    assert raised, text
=== END AC cli-money-parse-invalid ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to standard output.
- Do not use floating point for money at any layer.
- Do not import a database driver in the `cli` package.
- Unknown commands are rejected before the store is opened.
