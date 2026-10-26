# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account delete`, which removes an account that has no transactions. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md |
| Provides | ledger account delete |
| Consumes | accounts.get, accounts.delete, transactions.list |

## Purpose

Remove an unused account. An account that still has transactions is protected.

## Trigger

`./ledger account delete <code>`

## Behavior

1. Require exactly one argument after `account delete`; otherwise exit 2.
2. Look up the account with `accounts.get`. An absent code exits 4.
3. List the account's transactions with `transactions.list`. If any exist, exit 3 and remove nothing.
4. Delete the account with `accounts.delete`.
5. Print `deleted` and then the code, one per line.

## Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Account deleted |
| 1 | Database unreachable |
| 2 | Wrong argument count |
| 3 | Account has transactions |
| 4 | Account absent |

## Database Interface

- `FEATURE-ACCOUNTS-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNTS-005` — write: delete an account - supplies: `account` - returns: `account`
- `FEATURE-TRANSACTIONS-003` — read: list transactions for an account - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC account-delete-unused ===
Intent: Deleting an account with no transactions exits 0, prints deleted and the code, and removes it.

import csv
import io

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTDEL1"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Probe")
    code, out, err = cli_runner("account", "delete", acct)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [acct]]
    assert db.accounts.get(account=acct) is None
=== END AC account-delete-unused ===

=== AC account-delete-in-use ===
Intent: Deleting an account that has transactions exits 3, prints nothing, and keeps the account and its transaction.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTDEL2"
cat = "UTDELC2"
txn_id = 950001
with db_session() as db:
    db.accounts.create(account=acct, name="In Use")
    db.categories.create(category=cat, description="Delete Probe")
    db.transactions.create(
        txn_id=txn_id, date="2098-01-01", account=acct, category=cat, amount=900, memo="d"
    )
    code, out, err = cli_runner("account", "delete", acct)
    assert code == 3
    assert out == ""
    assert db.accounts.get(account=acct) is not None
    assert db.transactions.get(txn_id=txn_id) is not None
=== END AC account-delete-in-use ===

=== AC account-delete-absent ===
Intent: Deleting an absent account exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "UTDELNONE"
with db_session() as db:
    assert db.accounts.get(account=absent) is None
    code, out, err = cli_runner("account", "delete", absent)
    assert code == 4
    assert out == ""
=== END AC account-delete-absent ===

=== AC account-delete-then-get ===
Intent: After a successful delete, account get for the same code exits 4.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTDEL3"
with db_session() as db:
    db.accounts.create(account=acct, name="Gone Soon")
    code, out, err = cli_runner("account", "delete", acct)
    assert code == 0
    code, out, err = cli_runner("account", "get", acct)
    assert code == 4
=== END AC account-delete-then-get ===

=== AC account-delete-usage ===
Intent: A wrong argument count exits 2 and removes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTDEL4"
with db_session() as db:
    db.accounts.create(account=acct, name="Usage Probe")
    code, out, err = cli_runner("account", "delete")
    assert code == 2
    code, out, err = cli_runner("account", "delete", acct, "extra")
    assert code == 2
    assert db.accounts.get(account=acct) is not None
=== END AC account-delete-usage ===

## User Acceptance

- None.

## Guardrails

- An account with transactions is never removed.
- A refused or failed command removes nothing and writes nothing to standard output.
