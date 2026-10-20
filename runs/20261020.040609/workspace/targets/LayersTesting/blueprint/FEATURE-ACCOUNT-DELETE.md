# FEATURE: Account Delete

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Delete an account that has no transactions through `ledger account delete <code>`. |
| Depends On  | DATABASE.md, FEATURE-ACCOUNT-RENAME.md, FEATURE-NONNEGATIVE-BALANCE.md |
| Provides    | ledger account delete |
| Consumes    | accounts.get, transactions.list, accounts.delete |

## Purpose

`ledger account delete <code>` removes an account that no transaction references. An account that
still has transactions is never removed, and no transaction is changed or removed to make room.

## Behavior

- Validate `<code>` with the code rule: 1 to 12 characters from `A-Z` and `0-9`. An invalid code
  exits 3.
- Read the account. An absent code exits 4 and writes nothing.
- Read the transactions. If any transaction names the account, exit 3 and change nothing.
- Otherwise delete the account row inside the command's transaction, commit, then write the header
  `deleted` and the code.
- On any failure, write nothing to standard output and one diagnostic line to standard error.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC account-delete-removes ===
Intent: Deleting an account with no transactions exits 0, writes deleted then the code, and removes the account row.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH9"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Event Float")

exit_code, out, err = cli_runner("account", "delete", account_code)
print(out)
print(err)
assert exit_code == 0
assert out.splitlines() == ["deleted", account_code]
with db_session(dsn) as db:
    assert account_code not in [row.account for row in db.accounts.list()]
=== END AC account-delete-removes ===

=== AC account-delete-refuses-in-use ===
Intent: Deleting an account that has a transaction exits 3, writes nothing, and leaves the account row in place.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH9"
category_code = "SALES"
date_value = "2026-04-01"
seeded_cents = 4550
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Event Float")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=1, date=date_value, account=account_code, category=category_code,
        amount=seeded_cents, memo="seed",
    )

exit_code, out, err = cli_runner("account", "delete", account_code)
print(out)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert account_code in [row.account for row in db.accounts.list()]
=== END AC account-delete-refuses-in-use ===

=== AC account-delete-absent ===
Intent: Deleting an account code that does not exist exits 4 and writes nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
absent_code = "NOSUCH"
with db_session(dsn) as db:
    account_count_before = len(db.accounts.list())

exit_code, out, err = cli_runner("account", "delete", absent_code)
print(out)
print(err)
assert exit_code == 4
assert out == ""
with db_session(dsn) as db:
    assert len(db.accounts.list()) == account_count_before
=== END AC account-delete-absent ===

=== AC account-delete-invalid-code ===
Intent: A code that breaks the code rule exits 3 and changes no account row.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH9"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Event Float")
bad_code = "cash-9"

exit_code, out, err = cli_runner("account", "delete", bad_code)
print(out)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert account_code in [row.account for row in db.accounts.list()]
=== END AC account-delete-invalid-code ===

## User Acceptance

- None.

## Guardrails

- A transaction is never deleted, moved, or reassigned to allow an account deletion.
- An account is never deleted while any transaction names it.
- The deletion writes no output other than the `deleted` header and the code.
