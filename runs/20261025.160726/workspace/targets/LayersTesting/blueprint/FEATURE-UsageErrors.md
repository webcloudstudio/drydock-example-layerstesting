# FEATURE: Usage Errors

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Every unknown command, unknown table or report, and wrong argument count exits 2 with nothing on standard output. |
| Depends On | FEATURE-CliEntry.md, FEATURE-Count.md, FEATURE-LoadAccounts.md, FEATURE-AccountAdd.md, FEATURE-TxnPost.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md |
| Provides | usage error contract |
| Consumes | cli.main, ledger count, ledger load accounts, ledger account add, ledger txn post, ledger transfer, ledger report balances |

## Purpose

`ledger` distinguishes a malformed invocation (exit `2`) from a rejected one (exit `3`). A usage
error is detected from the argument vector alone, before the database is opened and before any
file is read, so it can never touch the store.

## Behavior

| Invocation | Exit |
|---|---|
| no arguments | `2` |
| unknown top-level command | `2` |
| `load` with a table other than `accounts`, `categories`, `transactions` | `2` |
| `report` with a report other than `balances`, `categories`, `monthly` | `2` |
| `account` or `txn` with an unknown subcommand | `2` |
| any command with too few or too many arguments | `2` |

Argument counts: `init` 0, `count` 0, `load` 2, `account add` 2, `account get` 1,
`account rename` 2, `account delete` 1, `txn post` 4 or 5, `txn get` 1, `txn amend` 2,
`txn delete` 1, `transfer` 4, `report` 1.

A usage error writes nothing to standard output and one diagnostic line to standard error.

## Database Interface

- None — persistence is owned by FEATURE-Count.md.

## Programmatic Acceptance

=== AC usage-unknown-command ===
Intent: An unknown command exits 2 with empty standard output and a single diagnostic line.
Requires: executable=python3; scope=test

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate")
print(out)
print(err)
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC usage-unknown-command ===

=== AC usage-no-arguments ===
Intent: Invoking the ledger with no arguments is a usage error.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(out)
print(err)
assert code == 2
assert out == ""
=== END AC usage-no-arguments ===

=== AC usage-unknown-targets ===
Intent: An unknown load table, report, account subcommand, or txn subcommand each exits 2.

from cli.testing import cli_runner

cases = [
    ("load", "nosuch", "ignored.csv"),
    ("report", "nosuch"),
    ("account", "frobnicate"),
    ("txn", "frobnicate"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code)
    assert code == 2, args
    assert out == "", args
=== END AC usage-unknown-targets ===

=== AC usage-wrong-argument-count ===
Intent: Too few or too many arguments for each command exits 2 before any work is done.

from cli.testing import cli_runner

cases = [
    ("init", "extra"),
    ("count", "extra"),
    ("load",),
    ("load", "accounts"),
    ("load", "accounts", "a.csv", "b.csv"),
    ("account", "add"),
    ("account", "add", "ONLYCODE"),
    ("account", "add", "CODE", "Name", "extra"),
    ("account", "get"),
    ("account", "rename", "CODE"),
    ("account", "delete"),
    ("txn", "post", "ACCT", "CAT", "1.00"),
    ("txn", "post", "ACCT", "CAT", "1.00", "2026-04-01", "memo", "extra"),
    ("txn", "get"),
    ("txn", "amend", "1"),
    ("txn", "delete"),
    ("transfer", "FROM", "TO", "1.00"),
    ("transfer", "FROM", "TO", "1.00", "2026-04-01", "extra"),
    ("report",),
    ("report", "balances", "extra"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code)
    assert code == 2, args
    assert out == "", args
=== END AC usage-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- A usage error never opens the database and never reads a file.
- A usage error never writes to standard output.
- Exit `2` is reserved for usage errors; rejected input is exit `3`.
