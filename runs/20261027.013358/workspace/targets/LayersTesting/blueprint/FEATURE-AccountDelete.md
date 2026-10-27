# FEATURE: Account Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account delete <code>`, refusing deletion while the account has transactions. |
| Depends On | FEATURE-AccountRename.md, FEATURE-LoadTransactions.md, DATABASE.md |
| Provides | ledger account delete |
| Consumes | ledger account rename, ledger load transactions |

## Purpose

Remove an account that has no transactions. The command is part of `cli/commands/account.py` and shares its verb table with add, get and rename.

## Behavior

1. `ledger account delete <code>` takes exactly one argument; any other count is a usage error (exit 2).
2. An absent code exits 4 with nothing on standard output.
3. An account referenced by any transaction is refused with exit 3 and nothing changes.
4. Otherwise the account row is deleted and the command prints `deleted` then the code, one per line.
5. The in-use check and the delete happen before any other write and in one database transaction.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC acct-delete-unused ===
Intent: Deleting an account with no transactions prints deleted and the code, and a separate read finds it gone.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code = "ZZADEL1"
with db_session() as db:
    db.accounts.create(account=code, name="Delete Me")
    exit_code, out, err = cli_runner("account", "delete", code)
    print(out)
    print(err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["deleted"], [code]]
    assert db.accounts.get(account=code) is None
=== END AC acct-delete-unused ===

=== AC acct-delete-in-use ===
Intent: An account referenced by a transaction is refused with exit 3, writes nothing to stdout, and both rows survive.

from cli.testing import cli_runner
from persistence.testing import db_session

code = "ZZADEL2"
cat = "ZZADCAT2"
with db_session() as db:
    db.accounts.create(account=code, name="In Use")
    db.categories.create(category=cat, description="In Use Cat")
    existing = db.transactions.list()
    txn_id = max([r.txn_id for r in existing], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-05-01", account=code, category=cat, amount=500, memo="held"
    )
    exit_code, out, err = cli_runner("account", "delete", code)
    print(out)
    print(err)
    assert exit_code == 3
    assert out == ""
    assert db.accounts.get(account=code) is not None
    assert db.transactions.get(txn_id=txn_id) is not None
=== END AC acct-delete-in-use ===

=== AC acct-delete-absent ===
Intent: Deleting an account that does not exist exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

code = "ZZADNONE"
with db_session() as db:
    assert db.accounts.get(account=code) is None
    exit_code, out, err = cli_runner("account", "delete", code)
    print(out)
    print(err)
    assert exit_code == 4
    assert out == ""
=== END AC acct-delete-absent ===

=== AC acct-delete-usage ===
Intent: Calling delete with no code is a usage error with exit 2 and nothing on standard output.

from cli.testing import cli_runner

exit_code, out, err = cli_runner("account", "delete")
print(out)
print(err)
assert exit_code == 2
assert out == ""
=== END AC acct-delete-usage ===

## User Acceptance

- None.

## Guardrails

- A refused or failed delete changes nothing.
- Diagnostics go to standard error only; standard output is empty on failure.
- No database driver is opened outside the persistence package.
