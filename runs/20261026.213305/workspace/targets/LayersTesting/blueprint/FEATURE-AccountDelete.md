# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger account delete <code>`, which removes an account that has no transactions. |
| Depends On | FEATURE-AccountGet.md, FEATURE-TxnPost.md, FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger account delete |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected, ledger txn post |

## Purpose

Delete one account by code. An account that still has transactions is refused so that no transaction is orphaned. Source Rule 1 applies: the command checks everything before its single write.

## Behavior

- Invocation: `ledger account delete <code>` with exactly one argument.
- The account is looked up through `db.accounts.get`. An absent code exits 4 with nothing on stdout.
- Transactions of the account are listed through `db.transactions.list(account=<code>)`. If any exist, the command exits 3 and changes nothing.
- Otherwise the account is removed with `db.accounts.delete` and the command writes two CSV lines to stdout: `deleted`, then the code. No header row beyond that pair.
- Failures write nothing to stdout and one diagnostic line to stderr.
- The existence check, the transaction check and the delete run in one database transaction.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: look up the account - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-003` — read: list the account's transactions - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNT-005` — write: delete the account - supplies: `account` - returns: `account`

## Programmatic Acceptance

=== AC account-delete-empty ===
Intent: Deleting an account with no transactions prints deleted and the code, and the account is gone.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code_ = "ZQAD01"
with db_session() as db:
    db.accounts.create(account=code_, name="Empty Account")
    code, out, err = cli_runner("account", "delete", code_)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [code_]]
    assert db.accounts.get(account=code_) is None
=== END AC account-delete-empty ===

=== AC account-delete-in-use ===
Intent: An account that has a transaction is refused with exit 3 and both records remain.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAD02"
cat = "ZQADC02"
txn_id = 910002
with db_session() as db:
    db.accounts.create(account=acct, name="Busy Account")
    db.categories.create(category=cat, description="Busy Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo=""
    )
    code, out, err = cli_runner("account", "delete", acct)
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert db.accounts.get(account=acct) is not None
    assert db.transactions.get(txn_id=txn_id) is not None
=== END AC account-delete-in-use ===

=== AC account-delete-absent ===
Intent: Deleting an absent account exits 4 with nothing on stdout and leaves other accounts alone.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "ZQAD03X"
other = "ZQAD03"
with db_session() as db:
    db.accounts.create(account=other, name="Bystander")
    before = len(db.accounts.list())
    code, out, err = cli_runner("account", "delete", absent)
    print(out)
    print(err)
    assert code == 4
    assert out == ""
    assert len(db.accounts.list()) == before
    assert db.accounts.get(account=other) is not None
=== END AC account-delete-absent ===

=== AC account-delete-after-txn-removed ===
Intent: Once its only transaction is removed, the account can be deleted.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAD04"
cat = "ZQADC04"
txn_id = 910004
with db_session() as db:
    db.accounts.create(account=acct, name="Cleared Account")
    db.categories.create(category=cat, description="Cleared Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=500, memo=""
    )
    code, out, err = cli_runner("account", "delete", acct)
    assert code == 3
    db.transactions.delete(txn_id=txn_id)
    code, out, err = cli_runner("account", "delete", acct)
    print(out)
    print(err)
    assert code == 0
    assert db.accounts.get(account=acct) is None
=== END AC account-delete-after-txn-removed ===

## User Acceptance

- None.

## Guardrails

- Never delete a transaction as a side effect of deleting an account.
- A failing command writes nothing to stdout and never echoes a DSN or credential.
- Database access goes only through the generated persistence package.
