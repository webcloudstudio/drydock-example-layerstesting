# FEATURE: Account Rename

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Rename an existing account by code and print the updated account row. |
| Depends On  | DATABASE.md, FEATURE-CLI-Dispatch.md, FEATURE-CLI-Output.md, FEATURE-Code-Validation.md, FEATURE-Command-Transaction.md |
| Provides    | ledger account rename <code> <name> |
| Consumes    | accounts.get, accounts.update |

## Purpose

`ledger account rename <code> <name>` changes the name of an existing account. It validates the
code and the new name, looks up the account, updates its name, and prints the updated row.

## Behavior

- The command runs inside one command transaction (FEATURE-Command-Transaction.md).
- The `<code>` argument is validated as an account code (FEATURE-Code-Validation.md) before any lookup.
- The `<name>` argument is validated as an account name: 1 to 40 characters, no comma, no newline.
  An invalid name exits 3 with no change.
- The account is looked up with `accounts.get`. An absent code exits 4 with no change.
- On success the name is written with `accounts.update` and the updated row is printed through the
  CSV output contract (FEATURE-CLI-Output.md) as:

  ```text
  account,name,transactions,balance
  <code>,<new name>,<transaction count>,<balance>
  ```

- The transaction count and balance are computed from the account's transactions by query, never
  embedded.

## Routes and Interfaces

| Command | Exit 0 | Exit 3 | Exit 4 |
|---|---|---|---|
| `ledger account rename <code> <name>` | updated row | invalid code or name | absent code |

## Database Interface

- `FEATURE-ACCOUNT-002` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-004` — write: update account name - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC account-rename-updates-name ===
Intent: Renaming an existing account stores the new name and the read-back row shows it.
Suite: scoped

from cli.testing import cli_runner
from persistence.testing import db_session

code, out, _ = None, None, None
with db_session() as db:
    db.accounts.create(account="CASH9", name="Event Float")
    code, out, _ = cli_runner("account", "rename", "CASH9", "Event Cash Box")
    row = db.accounts.get(account="CASH9")

assert code == 0
assert out == "account,name,transactions,balance\nCASH9,Event Cash Box,0,0.00\n"
assert row.name == "Event Cash Box"
=== END AC account-rename-updates-name ===

=== AC account-rename-absent-exits-4 ===
Intent: Renaming an absent account exits 4 and writes nothing to stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, _ = cli_runner("account", "rename", "NOSUCH", "Anything")
    row = db.accounts.get(account="NOSUCH")

assert code == 4
assert out == ""
assert row is None
=== END AC account-rename-absent-exits-4 ===

=== AC account-rename-invalid-name-exits-3 ===
Intent: A name longer than 40 characters is rejected with exit 3 and the stored name is unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

too_long = "X" * 41
with db_session() as db:
    db.accounts.create(account="CASH9", name="Event Float")
    code, out, _ = cli_runner("account", "rename", "CASH9", too_long)
    row = db.accounts.get(account="CASH9")

assert code == 3
assert out == ""
assert row.name == "Event Float"
=== END AC account-rename-invalid-name-exits-3 ===

=== AC account-rename-invalid-code-exits-3 ===
Intent: A malformed account code is rejected with exit 3 before any lookup.

from cli.testing import cli_runner

code, out, _ = cli_runner("account", "rename", "bad code!", "Name")

assert code == 3
assert out == ""
=== END AC account-rename-invalid-code-exits-3 ===

## User Acceptance

- None.

## Guardrails

- Every value written or printed comes from a query; no account name or count is hardcoded.
- Application code reaches the database only through `persistence` operations.
