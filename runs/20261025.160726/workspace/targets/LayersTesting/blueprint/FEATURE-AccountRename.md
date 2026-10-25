# FEATURE: Account Rename

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account rename <code> <name>`, changing only the account name. |
| Depends On | FEATURE-AccountGet.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger account rename |
| Consumes | accounts.update, transactions.list |

## Purpose

Rename an existing account. Only the name changes; the code, transactions, and balance are untouched.

## Command Contract

| Aspect | Rule |
|--------|------|
| Invocation | `ledger account rename <code> <name>` with exactly two arguments. |
| Validation | The name is 1 to 40 characters and contains no comma or newline. It is checked before any write. |
| Success stdout | Header `account,name,transactions,balance`, then the updated account row. |
| Invalid name | Exit 3, nothing on stdout, the stored name unchanged. |
| Absent account | Exit 4, nothing on stdout. |
| Wrong argument count | Exit 2, nothing on stdout. |

## Database Interface

- `FEATURE-ACCOUNT-004` — write: rename an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: list the account's transactions for the printed count and balance - supplies: `account` - returns: `amount`

## Programmatic Acceptance

=== AC account-rename-success ===
Intent: Renaming an account prints the updated row and the new name reads back from storage.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ARENA1"
    before = "Old Name"
    after = "New Name"
    db.accounts.create(account=code, name=before)
    rc, out, err = cli_runner("account", "rename", code, after)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert rows[1][0] == code
    assert rows[1][1] == after
    assert int(rows[1][2]) == 0
    got = db.accounts.get(account=code)
    assert got is not None
    assert got.name == after
=== END AC account-rename-success ===

=== AC account-rename-keeps-transactions ===
Intent: Renaming leaves the account's transactions and balance untouched.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ARENT1"
    cat = "ARENTC1"
    db.accounts.create(account=code, name="Before")
    db.categories.create(category=cat, description="Rename Cat")
    cents = 7777
    txn_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-05-01", account=code,
        category=cat, amount=cents, memo="keep",
    )
    rc, out, err = cli_runner("account", "rename", code, "After")
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert int(rows[1][2]) == 1
    assert int(rows[1][3].replace(".", "")) == cents
    kept = db.transactions.get(txn_id=txn_id)
    assert kept is not None
    assert kept.amount == cents
    assert kept.account == code
    assert kept.memo == "keep"
=== END AC account-rename-keeps-transactions ===

=== AC account-rename-absent ===
Intent: Renaming an absent account exits 4 and creates nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent = "ARENN1"
    assert db.accounts.get(account=absent) is None
    rc, out, err = cli_runner("account", "rename", absent, "Whatever")
    print(err)
    assert rc == 4
    assert out == ""
    assert db.accounts.get(account=absent) is None
=== END AC account-rename-absent ===

=== AC account-rename-invalid-name ===
Intent: A name that is too long, empty, or contains a comma is rejected with exit 3 and the stored name is unchanged.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ARENI1"
    original = "Original"
    db.accounts.create(account=code, name=original)
    too_long = "N" * 41
    for bad in (too_long, "", "has,comma"):
        rc, out, err = cli_runner("account", "rename", code, bad)
        print(err)
        assert rc == 3
        assert out == ""
        got = db.accounts.get(account=code)
        assert got is not None
        assert got.name == original
=== END AC account-rename-invalid-name ===

=== AC account-rename-usage ===
Intent: Renaming with a wrong argument count exits 2 and writes nothing to stdout.

from cli.testing import cli_runner

for args in (("account", "rename"), ("account", "rename", "ONLYCODE"), ("account", "rename", "A", "B", "C")):
    rc, out, err = cli_runner(*args)
    assert rc == 2
    assert out == ""
=== END AC account-rename-usage ===

## User Acceptance

- None.

## Guardrails

- Only the name column changes; the code is never altered.
- Validation completes before the first write.
- Nothing is written to stdout on failure.
