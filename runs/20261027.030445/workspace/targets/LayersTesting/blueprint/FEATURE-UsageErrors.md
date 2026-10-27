# FEATURE: Usage Errors

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Every command, group, table, and report rejects unknown names and wrong argument counts with exit 2, empty standard output, and one diagnostic on standard error. |
| Depends On | FEATURE-LedgerCli.md, FEATURE-LedgerInit.md, FEATURE-LedgerCount.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-AccountAdd.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-AccountDelete.md, FEATURE-TxnPost.md, FEATURE-TxnGet.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-ReportBalances.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides | cli.usage-errors |
| Consumes | ledger, ledger init, ledger count, ledger load, ledger account add, ledger account get, ledger account rename, ledger account delete, ledger txn post, ledger txn get, ledger txn amend, ledger txn delete, ledger transfer, ledger report balances, ledger report categories, ledger report monthly |

## Purpose

This feature makes usage-error handling uniform. A usage error is an unknown top-level command, an unknown `account` or `txn` subcommand, an unknown `load` table, an unknown `report`, or a wrong argument count for any command. It exits `2`, writes nothing to standard output, writes one diagnostic line to standard error naming the expected argument form, and never writes to the database.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Behavior

| Invocation | Result |
|---|---|
| `ledger frobnicate` | exit 2 |
| `ledger` (no command) | exit 2 |
| `ledger account` / `ledger account nosuch ...` | exit 2 |
| `ledger txn` / `ledger txn nosuch ...` | exit 2 |
| `ledger load nosuch file.csv` | exit 2 |
| `ledger load accounts` (missing file) | exit 2 |
| `ledger report` / `ledger report nosuch` | exit 2 |
| `ledger report balances extra` | exit 2 |
| `ledger init extra` / `ledger count extra` | exit 2 |
| `ledger account add X` (missing name) | exit 2 |
| `ledger account get` (missing code) | exit 2 |
| `ledger txn post A B` (too few arguments) | exit 2 |
| `ledger txn get` / `ledger txn amend 1` / `ledger txn delete` | exit 2 |
| `ledger transfer A B 1.00` (missing date) | exit 2 |

Rules:

1. Every handler routes argument-form errors through the shared `UsageError` path of the CLI foundation.
2. Usage checks run before any database access and before any value validation, so a usage error never writes and never depends on stored rows.
3. The diagnostic names the expected form (for example `usage: ledger account get <code>`) and is written only to standard error.
4. Any handler found not to use the shared path is corrected in this story.

## Programmatic Acceptance

=== AC usage-unknown-command ===
Intent: An unknown top-level command exits 2 with empty standard output and a diagnostic on standard error.

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate")
print(out)
print(err)
assert code == 2
assert out == ""
assert err.strip() != ""
=== END AC usage-unknown-command ===

=== AC usage-no-command ===
Intent: Running with no command at all is a usage error.

from cli.testing import cli_runner

code, out, err = cli_runner()
print(out)
print(err)
assert code == 2
assert out == ""
=== END AC usage-no-command ===

=== AC usage-unknown-report ===
Intent: An unknown report name and a missing report name both exit 2 with empty standard output.

from cli.testing import cli_runner

for args in (("report", "nosuch"), ("report",)):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC usage-unknown-report ===

=== AC usage-unknown-table ===
Intent: Loading an unknown table, or omitting the file argument, exits 2 with empty standard output.

from cli.testing import cli_runner

for args in (("load", "nosuch", "file.csv"), ("load", "accounts"), ("load",)):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC usage-unknown-table ===

=== AC usage-unknown-subcommand ===
Intent: An unknown or missing subcommand under account and txn exits 2 with empty standard output.

from cli.testing import cli_runner

cases = [
    ("account",),
    ("account", "nosuch", "X"),
    ("txn",),
    ("txn", "nosuch", "1"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC usage-unknown-subcommand ===

=== AC usage-wrong-argument-count ===
Intent: Every command given too few or too many arguments exits 2 with empty standard output and a nonblank diagnostic.

from cli.testing import cli_runner

cases = [
    ("init", "extra"),
    ("count", "extra"),
    ("account", "add", "X"),
    ("account", "get"),
    ("account", "rename", "X"),
    ("account", "delete"),
    ("txn", "post", "A", "B"),
    ("txn", "get"),
    ("txn", "amend", "1"),
    ("txn", "delete"),
    ("transfer", "A", "B", "1.00"),
    ("report", "balances", "extra"),
    ("report", "categories", "extra"),
    ("report", "monthly", "extra"),
]
for args in cases:
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
    assert err.strip() != ""
=== END AC usage-wrong-argument-count ===

=== AC usage-writes-nothing ===
Intent: Usage errors change no stored record, shown by identical row counts before and after a batch of bad invocations.

import csv
import io
from cli.testing import cli_runner

def counts():
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return rows

before = counts()
for args in (("frobnicate",), ("txn", "post", "A", "B"), ("transfer", "A", "B", "1.00"), ("account", "add", "X")):
    code, out, err = cli_runner(*args)
    assert code == 2
after = counts()
assert after == before
=== END AC usage-writes-nothing ===

## User Acceptance

- None.

## Guardrails

- A usage error never writes to standard output.
- A usage error never opens a write path to the database.
- The diagnostic goes only to standard error; its wording is not part of the contract.
- No help command is added.
