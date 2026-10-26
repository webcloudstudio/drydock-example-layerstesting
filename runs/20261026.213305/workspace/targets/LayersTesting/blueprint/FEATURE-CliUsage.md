# FEATURE: CLI Usage

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Reject unknown commands, tables, reports and wrong argument counts with exit 2 and usage text on standard error only. |
| Depends On | FEATURE-CliFoundation.md, FEATURE-ErrorContract.md |
| Provides | ledger usage |
| Consumes | ledger.register_command, ledger_errors.UsageError |

## Purpose

Any invocation that is not a valid command shape exits 2 before any database access. The usage
text is derived from the command table and names every command and sub-verb.

## Rules

- No arguments, an unknown command, an unknown `load` table, an unknown `report`, an unknown sub-verb of `account` or `txn`, or the wrong number of arguments for a known command all raise `UsageError`, which the top-level handler maps to exit 2.
- Argument counts follow the command table: `init` 0, `count` 0, `load` 2, `account add` 2, `account get` 1, `account rename` 2, `account delete` 1, `txn post` 4 or 5, `txn get` 1, `txn amend` 2, `txn delete` 1, `transfer` 4, `report <name>` 0.
- Usage text goes to standard error only. It lists `init`, `count`, `load`, `account add|get|rename|delete`, `txn post|get|amend|delete`, `transfer`, and `report balances|categories|monthly`.
- Standard output stays empty and the database is neither opened nor changed.
- Argument-count validation happens before any value validation, so a command with a wrong count never exits 3.

## Database Interface

- None — this Blueprint reaches no repository.

## Programmatic Acceptance

=== AC usage-no-arguments ===
Intent: Running with no arguments exits 2 with nothing on standard output.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(err)
assert code == 2
assert out == ""
=== END AC usage-no-arguments ===

=== AC usage-unknown-command ===
Intent: An unknown command exits 2 with nothing on standard output.

from cli.testing import cli_runner

command = "frobnicate"
code, out, err = cli_runner(command)
print(err)
assert code == 2
assert out == ""
=== END AC usage-unknown-command ===

=== AC usage-unknown-report-and-table ===
Intent: An unknown report name and an unknown load table each exit 2.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "nosuch")
print(err)
assert code == 2 and out == ""
code, out, err = cli_runner("load", "nosuch", "ignored.csv")
print(err)
assert code == 2 and out == ""
=== END AC usage-unknown-report-and-table ===

=== AC usage-wrong-argument-count ===
Intent: Missing and surplus arguments exit 2 for known commands.

from cli.testing import cli_runner

cases = [
    ("init", "extra"),
    ("count", "extra"),
    ("account", "get"),
    ("account", "add", "ONLYCODE"),
    ("account", "bogus", "X"),
    ("txn", "get"),
    ("txn", "amend", "1"),
    ("txn", "post", "A", "B", "1.00"),
    ("transfer", "A", "B", "1.00"),
    ("report", "balances", "extra"),
    ("load", "accounts"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code, err)
    assert code == 2, args
    assert out == "", args
=== END AC usage-wrong-argument-count ===

=== AC usage-changes-nothing ===
Intent: A usage error leaves every table unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = (
        len(db.accounts.list()),
        len(db.categories.list()),
        len(db.transactions.list()),
    )
    code, out, err = cli_runner("account", "add", "ONLYCODE")
    assert code == 2
    after = (
        len(db.accounts.list()),
        len(db.categories.list()),
        len(db.transactions.list()),
    )
    assert after == before
=== END AC usage-changes-nothing ===

## User Acceptance

- None.

## Guardrails

- Usage text is written to standard error and never to standard output.
- A usage error never opens or changes the database.
