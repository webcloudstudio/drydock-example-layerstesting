# FEATURE: Account Duplicate Rejection

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Rejects `ledger account add` for a code that already exists, leaving the accounts table unchanged. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | duplicate account rejection |
| Consumes | accounts.list |

## Purpose

An account code is a primary key. Adding an existing code is a rejected command: it exits 3, writes
nothing to stdout, and neither the existing row nor any other row changes.

## Behavior

| Aspect | Rule |
|--------|------|
| Detection | The duplicate is detected by checking for the code before the first write, not by catching a late storage error. |
| Result | Exit 3, nothing on stdout, one diagnostic line on stderr. |
| State | The existing account keeps its original name; the account count is unchanged. |
| Recovery | A later add of a different code succeeds. |

## Database Interface

- `FEATURE-ACCOUNT-002` — read: check whether the code already exists - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-duplicate-rejected ===
Intent: Adding an existing account code exits 3, prints nothing, and keeps the original name.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ADUPR1"
    original = "Original Name"
    db.accounts.create(account=code, name=original)
    before = len(db.accounts.list())
    rc, out, err = cli_runner("account", "add", code, "Different Name")
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.accounts.list()) == before
    got = db.accounts.get(account=code)
    assert got is not None
    assert got.name == original
=== END AC account-duplicate-rejected ===

=== AC account-duplicate-same-name ===
Intent: Re-adding an existing account with the identical name is still rejected with exit 3.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ADUPS1"
    name = "Same Name"
    rc, out, err = cli_runner("account", "add", code, name)
    print(err)
    assert rc == 0
    before = len(db.accounts.list())
    rc, out, err = cli_runner("account", "add", code, name)
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.accounts.list()) == before
=== END AC account-duplicate-same-name ===

=== AC account-duplicate-then-recover ===
Intent: After a duplicate rejection, adding a different code succeeds and adds exactly one row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "ADUPV1"
    other = "ADUPV2"
    db.accounts.create(account=code, name="First")
    rc, out, err = cli_runner("account", "add", code, "Again")
    assert rc == 3
    before = len(db.accounts.list())
    rc, out, err = cli_runner("account", "add", other, "Second")
    print(err)
    assert rc == 0
    assert len(db.accounts.list()) == before + 1
    got = db.accounts.get(account=other)
    assert got is not None
    assert got.name == "Second"
=== END AC account-duplicate-then-recover ===

## User Acceptance

- None.

## Guardrails

- A rejected duplicate changes no row.
- Nothing is written to stdout on failure.
