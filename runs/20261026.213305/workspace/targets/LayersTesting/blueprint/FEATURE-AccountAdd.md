# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger account add <code> <name>` creating one new account. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-LedgerInit.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-ErrorContract.md |
| Provides | ledger account add |
| Consumes | ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected |

## Purpose

`ledger account add <code> <name>` stores a new account and prints its row.

## Behavior

- Arguments: exactly a code and a name; any other count is a usage error (exit 2).
- `code` is 1 to 12 characters of `A-Z0-9`; `name` is 1 to 40 characters with no comma or newline. Violations exit 3 and store nothing.
- A code already stored exits 3 and leaves the existing account unchanged. Names may repeat across accounts; only codes are unique.
- Success writes `account,name,transactions,balance` then the new row with `0` transactions and balance `0.00`. Exit 0.

## Database Interface

- `FEATURE-ACCOUNT-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: detect an existing code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-add-success ===
Intent: Adding an account prints its zero-activity row and the account reads back from the store.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code_value = "ZAA1A"
name = "Added Account"
with db_session() as db:
    assert db.accounts.get(account=code_value) is None
    code, out, err = cli_runner("account", "add", code_value, name)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [
        ["account", "name", "transactions", "balance"],
        [code_value, name, "0", "0.00"],
    ]
    got = db.accounts.get(account=code_value)
    assert got is not None and got.name == name
=== END AC account-add-success ===

=== AC account-add-duplicate-code ===
Intent: A duplicate code exits 3, writes nothing to standard output and leaves the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

code_value = "ZAA2A"
original = "Original Name"
other = "Different Name"
with db_session() as db:
    db.accounts.create(account=code_value, name=original)
    before = len(db.accounts.list())
    code, out, err = cli_runner("account", "add", code_value, other)
    print(code, out, err)
    assert code == 3
    assert out == ""
    assert db.accounts.get(account=code_value).name == original
    assert len(db.accounts.list()) == before
=== END AC account-add-duplicate-code ===

=== AC account-add-repeated-name ===
Intent: Two accounts with different codes may share one name.

from cli.testing import cli_runner
from persistence.testing import db_session

shared = "Shared Name"
first, second = "ZAA3A", "ZAA3B"
with db_session() as db:
    code, out, err = cli_runner("account", "add", first, shared)
    print(code, out, err)
    assert code == 0
    code, out, err = cli_runner("account", "add", second, shared)
    print(code, out, err)
    assert code == 0
    assert db.accounts.get(account=first).name == shared
    assert db.accounts.get(account=second).name == shared
=== END AC account-add-repeated-name ===

=== AC account-add-invalid-input ===
Intent: Invalid codes and names exit 3 and create nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

cases = [
    ("zaa4a", "Lowercase code"),
    ("ZAA-4", "Punctuation in code"),
    ("Z" * 13, "Code too long"),
    ("ZAA4B", ""),
    ("ZAA4C", "N" * 41),
    ("ZAA4D", "has,comma"),
]
with db_session() as db:
    before = len(db.accounts.list())
    for c, n in cases:
        code, out, err = cli_runner("account", "add", c, n)
        print(c, n, code, out, err)
        assert code == 3
        assert out == ""
    assert len(db.accounts.list()) == before
=== END AC account-add-invalid-input ===

=== AC account-add-wrong-argument-count ===
Intent: A wrong argument count is a usage error with exit 2 and nothing stored.

from cli.testing import cli_runner
from persistence.testing import db_session

code_value = "ZAA5A"
with db_session() as db:
    before = len(db.accounts.list())
    for args in (("account", "add"), ("account", "add", code_value), ("account", "add", code_value, "Name", "extra")):
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
    assert db.accounts.get(account=code_value) is None
    assert len(db.accounts.list()) == before
=== END AC account-add-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to standard output and nothing to the database.
- Only account codes are unique; names are not.
- Diagnostics never include a DSN or credential.
