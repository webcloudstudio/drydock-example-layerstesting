# FEATURE: Usage Errors

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Guarantee every unknown command, table, report, verb or wrong argument count exits 2 with a usage line on standard error only. |
| Depends On | FEATURE-Init.md, FEATURE-Count.md, FEATURE-LoadTransactions.md, FEATURE-AccountDelete.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-Transfer.md, FEATURE-ReportCategories.md, FEATURE-ReportMonthly.md |
| Provides | cli.usage |
| Consumes | ledger, ledger init, ledger count, ledger load accounts, ledger load categories, ledger load transactions, ledger account add, ledger account get, ledger account rename, ledger account delete, ledger txn post, ledger txn get, ledger txn amend, ledger txn delete, ledger transfer, ledger report balances, ledger report categories, ledger report monthly |

## Purpose

Integration story proving the usage-error contract across the whole command table.

## Usage Table

One shared usage table covers every command and sub-verb; a usage error prints that command's
one-line usage text to standard error.

| Command | Usage |
|---------|-------|
| `init` | `ledger init` |
| `count` | `ledger count` |
| `load` | `ledger load <accounts\|categories\|transactions> <csv>` |
| `account add` / `get` / `rename` / `delete` | `ledger account add <code> <name>`, `get <code>`, `rename <code> <name>`, `delete <code>` |
| `txn post` / `get` / `amend` / `delete` | `ledger txn post <account> <category> <amount> <date> [<memo>]`, `get <id>`, `amend <id> <amount>`, `delete <id>` |
| `transfer` | `ledger transfer <from> <to> <amount> <date>` |
| `report` | `ledger report <balances\|categories\|monthly>` |

## Behavior

- `ledger` with no arguments, an unknown command, unknown table, unknown report, unknown verb, or
  wrong argument count exits 2.
- Standard output is empty; standard error carries the usage text.
- Argument-count checks happen before any database access, so a usage error never reads or writes
  the database.
- Invalid values of correct arity (for example a non-digit transaction id) are rejections (exit 3),
  and absent records are not found (exit 4); neither is a usage error.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC usage-table ===
Intent: Every unknown command, table, report, verb and wrong argument count exits 2 with empty stdout, a diagnostic on stderr, and no row changes.

from persistence.testing import db_session
from cli.testing import cli_runner

cases = [
    [],
    ["frobnicate"],
    ["init", "extra"],
    ["count", "extra"],
    ["load"],
    ["load", "accounts"],
    ["load", "nosuch", "file.csv"],
    ["load", "accounts", "file.csv", "extra"],
    ["account"],
    ["account", "frob"],
    ["account", "add"],
    ["account", "add", "ONLY"],
    ["account", "get"],
    ["account", "rename", "ONLY"],
    ["account", "delete"],
    ["txn"],
    ["txn", "frob"],
    ["txn", "post", "A", "B"],
    ["txn", "get"],
    ["txn", "amend", "1"],
    ["txn", "delete"],
    ["transfer", "A", "B", "1.00"],
    ["report"],
    ["report", "nosuch"],
    ["report", "balances", "extra"],
    ["report", "categories", "extra"],
    ["report", "monthly", "extra"],
]
with db_session() as db:
    before = (len(db.accounts.list()), len(db.categories.list()), len(db.transactions.list()))
    for args in cases:
        code, out, err = cli_runner(*args)
        print(args, code, repr(out), repr(err))
        assert code == 2
        assert out == ""
        assert err.strip() != ""
    after = (len(db.accounts.list()), len(db.categories.list()), len(db.transactions.list()))
    assert after == before
=== END AC usage-table ===

=== AC usage-executable ===
Intent: The ledger executable at the application root exits 2 with empty stdout for no arguments and for an unknown command.

import subprocess

for args in ([], ["frobnicate"], ["report", "nosuch"]):
    result = subprocess.run(["./ledger", *args], capture_output=True, text=True)
    print(args, result.returncode, repr(result.stdout), repr(result.stderr))
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""
=== END AC usage-executable ===

=== AC usage-not-confused-with-rejection ===
Intent: Correct arity with an invalid value exits 3, and correct arity naming an absent record exits 4, never 2.

from cli.testing import cli_runner

code, out, err = cli_runner("txn", "get", "abc")
print(code, out, err)
assert code == 3
assert out == ""

code, out, err = cli_runner("account", "get", "ZZNOSUCH9")
print(code, out, err)
assert code == 4
assert out == ""

code, out, err = cli_runner("txn", "get", "99999999999")
print(code, out, err)
assert code == 4
assert out == ""
=== END AC usage-not-confused-with-rejection ===

## User Acceptance

- None.

## Guardrails

- A usage error never writes to standard output.
- Usage errors never open or modify the database.
- Usage text is a single line per command on standard error and is never compared by the grader.
