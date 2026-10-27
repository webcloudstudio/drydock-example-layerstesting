# FEATURE: Ledger Init

| Field       | Value |
|-------------|-------|
| Version     | 20261027 V1 |
| Description | The `ledger init` command resets the ledger to empty. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-LedgerCli.md |
| Provides    | ledger init |
| Consumes    | ledger |

## Purpose

`ledger init` prepares an empty ledger for loading and use and removes existing ledger records when rerun.

## Behavior

- Takes no arguments; any argument is a usage error (exit 2).
- Removes every transaction first, then every category and every account, in one persistence-library transaction, so foreign keys hold and the unit is atomic.
- Writes nothing to standard output and exits 0. Rerunning it removes all records again.
- Applies no DDL. If the database cannot be opened it exits 1 and changes nothing.
- The handler returns `None` and is registered as `("init",)`.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC init-empties-all-tables ===
Intent: After init succeeds with empty standard output, accounts, categories, and transactions read back as empty even though rows existed before.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="ZQI1", name="Init Account")
    db.categories.create(category="ZQI1", description="Init Category")
    db.transactions.create(
        txn_id=920001, date="2026-06-01", account="ZQI1", category="ZQI1", amount=1000, memo=""
    )
    assert db.transactions.get(txn_id=920001) is not None
    code, out, err = cli_runner("init")
    print(out)
    print(err)
    assert code == 0
    assert out == ""
    assert db.transactions.list() == []
    assert db.categories.list() == []
    assert db.accounts.list() == []
=== END AC init-empties-all-tables ===

=== AC init-rerun-is-repeatable ===
Intent: Running init a second time after new rows are added removes them again and still exits 0 with empty output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    assert out == ""
    db.accounts.create(account="ZQI2", name="Second Account")
    assert db.accounts.get(account="ZQI2") is not None
    code, out, err = cli_runner("init")
    print(out)
    print(err)
    assert code == 0
    assert out == ""
    assert db.accounts.get(account="ZQI2") is None
    assert db.accounts.list() == []
=== END AC init-rerun-is-repeatable ===

=== AC init-rejects-arguments ===
Intent: init with an extra argument is a usage error that writes nothing and removes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    db.accounts.create(account="ZQI3", name="Keep Account")
    code, out, err = cli_runner("init", "extra")
    print(out)
    print(err)
    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert db.accounts.get(account="ZQI3") is not None
=== END AC init-rejects-arguments ===

=== AC init-store-unavailable ===
Intent: When the database cannot be opened, init exits 1 with empty standard output.

import os
import shutil
import tempfile

from cli.testing import cli_runner

base = tempfile.mkdtemp()
bad_path = os.path.join(base, "missing-dir", "ledger.db")
saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "DATABASE_PATH")}
try:
    os.environ["DATABASE_URL"] = bad_path
    os.environ.pop("DATABASE_PATH", None)
    code, out, err = cli_runner("init")
    print(out)
    print(err)
    assert code == 1
    assert out == ""
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    shutil.rmtree(base, ignore_errors=True)
=== END AC init-store-unavailable ===

## User Acceptance

- None.

## Guardrails

- `init` applies no DDL and never drops or recreates tables.
- `init` writes nothing to standard output.
- Delete transactions before categories and accounts.
