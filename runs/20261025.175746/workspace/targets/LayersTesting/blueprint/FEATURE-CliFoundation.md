# FEATURE: CLI Foundation

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | The ledger executable, command dispatch, exit-code mapping, CSV output, and shared input validators. |
| Depends On | DATABASE.md, ARCHITECTURE.md |
| Provides | ledger, cli.main, cli.testing.cli_runner, cli.errors, cli.validate, cli.money, cli.output, cli.registry |

## Purpose

Provide the executable and the shared machinery every command uses, so command stories write only
their own behavior.

## Interface

| Module | Contract |
|---|---|
| `ledger` | Executable at the application root; runs `cli.main(sys.argv[1:])` and exits with the result. |
| `cli/__init__.py` | `main(argv: list[str] \| None = None) -> int`. |
| `cli/testing.py` | `cli_runner(*args) -> (exit_code, stdout, stderr)` without spawning a process. |
| `cli/errors.py` | `LedgerError` with an `exit_code` attribute; subclasses `Operational` (1), `Usage` (2), `Rejected` (3), `NotFound` (4). |
| `cli/registry.py` | `register(path, min_args, max_args, handler)` and `COMMANDS`. A handler is `run(db, args) -> list[list[str]]` returning the header and data rows. |
| `cli/commands/` | Every module is imported at startup; each registers its handlers. |
| `cli/database.py` | `open_ledger()` opens the store with `open_database`, using `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`. |
| `cli/validate.py` | `validate_code`, `validate_name`, `validate_memo`, `validate_date`; each returns the value or raises `Rejected`. |
| `cli/money.py` | `parse_amount(text) -> int` cents and `format_amount(cents) -> str`, integer arithmetic only. |
| `cli/output.py` | `write_rows(rows)` writes comma-separated rows with `\n` endings and no quoting; `TRANSACTION_HEADER`, `format_transaction(row)`. |

## Behavior

- The dispatcher resolves the command path and checks the argument count before opening the
  database. An unknown command, unknown table or report, or wrong argument count exits 2.
- A `LedgerError` is mapped to its exit code; the message goes to standard error as one line and
  nothing is written to standard output. Any other database failure exits 1.
- Output is written only after the handler returns, so a failing command writes nothing to
  standard output.
- Codes are 1 to 12 characters from `A-Z` and `0-9`. Names are 1 to 40 characters. Memos are 0 to
  60 characters. None contains a comma or newline. Dates are real calendar dates `YYYY-MM-DD`.
- Amounts match `-?DIGITS[.D[D]]`, never zero. Output amounts have exactly two decimals, a leading
  `-` when negative, and no thousands separator.
- A non-integer transaction id is rejected with exit 3 (disclosed decision Q-003).

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC clifoundation-executable ===
Intent: The ledger executable exists at the application root and is executable.

import os

assert os.path.isfile("ledger")
assert os.access("ledger", os.X_OK)
=== END AC clifoundation-executable ===

=== AC clifoundation-usage-process ===
Intent: Running the executable with an unknown command exits 2 and writes nothing to standard output.

import os
import subprocess

result = subprocess.run(
    ["./ledger", "frobnicate"], capture_output=True, text=True, env={**os.environ}
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC clifoundation-usage-process ===

=== AC clifoundation-usage-unknown-report ===
Intent: An unknown report exits 2 with no standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "nosuchreport")
print(err)
assert code == 2
assert out == ""
=== END AC clifoundation-usage-unknown-report ===

=== AC clifoundation-usage-unknown-table ===
Intent: Loading an unknown table exits 2 with no standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("load", "nosuchtable", "missing.csv")
print(err)
assert code == 2
assert out == ""
=== END AC clifoundation-usage-unknown-table ===

=== AC clifoundation-usage-argcount ===
Intent: A wrong argument count exits 2 with no standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("account", "get")
print(err)
assert code == 2
assert out == ""

code, out, err = cli_runner("count", "extra")
print(err)
assert code == 2
assert out == ""
=== END AC clifoundation-usage-argcount ===

=== AC clifoundation-usage-no-command ===
Intent: Running with no command at all is a usage error.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(err)
assert code == 2
assert out == ""
=== END AC clifoundation-usage-no-command ===

=== AC clifoundation-error-exit-codes ===
Intent: The error classes carry the exit codes 1, 2, 3, and 4.

from cli import errors

assert issubclass(errors.Operational, errors.LedgerError)
assert issubclass(errors.Usage, errors.LedgerError)
assert issubclass(errors.Rejected, errors.LedgerError)
assert issubclass(errors.NotFound, errors.LedgerError)
assert errors.Operational("x").exit_code == 1
assert errors.Usage("x").exit_code == 2
assert errors.Rejected("x").exit_code == 3
assert errors.NotFound("x").exit_code == 4
=== END AC clifoundation-error-exit-codes ===

=== AC clifoundation-amount-roundtrip ===
Intent: Amounts parse to integer cents and format back to the same two-decimal text.

from cli.money import format_amount, parse_amount

for text in ("5000.00", "-12.50", "45.07"):
    cents = parse_amount(text)
    assert isinstance(cents, int)
    assert format_amount(cents) == text
=== END AC clifoundation-amount-roundtrip ===

=== AC clifoundation-amount-short-forms ===
Intent: Amounts with fewer than two decimals parse to the same cents as their padded form.

from cli.money import parse_amount

assert parse_amount("12.5") == parse_amount("12.50")
assert parse_amount("7") == parse_amount("7.00")
assert parse_amount("-3.1") == parse_amount("-3.10")
=== END AC clifoundation-amount-short-forms ===

=== AC clifoundation-amount-rejections ===
Intent: Zero, three decimals, and non-numeric amounts are rejected with exit code 3.

from cli.errors import Rejected
from cli.money import parse_amount

for text in ("0", "0.00", "-0", "1.234", "abc", "", "1,00", "+5.00", ".5"):
    try:
        parse_amount(text)
    except Rejected as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError(f"accepted {text!r}")
=== END AC clifoundation-amount-rejections ===

=== AC clifoundation-date-validation ===
Intent: A real calendar date is accepted unchanged and an impossible date is rejected.

from cli.errors import Rejected
from cli.validate import validate_date

good = "2026-02-28"
assert validate_date(good) == good
for bad in ("2026-02-30", "2026-13-01", "26-01-01", "2026/01/01", ""):
    try:
        validate_date(bad)
    except Rejected:
        pass
    else:
        raise AssertionError(f"accepted {bad!r}")
=== END AC clifoundation-date-validation ===

=== AC clifoundation-code-validation ===
Intent: Codes of 1 to 12 characters from A-Z and 0-9 are accepted; others are rejected.

from cli.errors import Rejected
from cli.validate import validate_code

for good in ("A", "DRAWER1", "ABCDEFGHIJKL"):
    assert validate_code(good) == good
for bad in ("", "lower", "ABCDEFGHIJKLM", "A-B", "A B"):
    try:
        validate_code(bad)
    except Rejected:
        pass
    else:
        raise AssertionError(f"accepted {bad!r}")
=== END AC clifoundation-code-validation ===

=== AC clifoundation-text-validation ===
Intent: Names are 1 to 40 characters and memos 0 to 60 characters, with no comma or newline.

from cli.errors import Rejected
from cli.validate import validate_memo, validate_name

name = "Front Drawer"
assert validate_name(name) == name
assert validate_memo("") == ""
assert validate_name("n" * 40) == "n" * 40
assert validate_memo("m" * 60) == "m" * 60
for call, bad in (
    (validate_name, ""),
    (validate_name, "n" * 41),
    (validate_name, "a,b"),
    (validate_name, "a\nb"),
    (validate_memo, "m" * 61),
    (validate_memo, "a,b"),
    (validate_memo, "a\nb"),
):
    try:
        call(bad)
    except Rejected:
        pass
    else:
        raise AssertionError(f"accepted {bad!r}")
=== END AC clifoundation-text-validation ===

=== AC clifoundation-transaction-format ===
Intent: A transaction row formats to the declared six CSV fields with a two-decimal amount.

from types import SimpleNamespace

from cli.money import format_amount
from cli.output import TRANSACTION_HEADER, format_transaction

row = SimpleNamespace(
    txn_id=77, date="2026-04-01", account="DRAWER1", category="SALES", amount=4550, memo="walk in"
)
fields = format_transaction(row)
assert list(TRANSACTION_HEADER) == ["txn_id", "date", "account", "category", "amount", "memo"]
assert fields == [
    str(row.txn_id), row.date, row.account, row.category, format_amount(row.amount), row.memo,
]
=== END AC clifoundation-transaction-format ===

## User Acceptance

- None.

## Guardrails

- Diagnostics go to standard error and are never compared; standard output carries only CSV.
- A failing command writes nothing to standard output.
- No floating point is used for money.
- No database driver is imported outside the shipped persistence library.
