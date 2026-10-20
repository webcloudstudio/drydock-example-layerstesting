# FEATURE: Account Lifecycle

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide account creation, retrieval, renaming, and deletion operations. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CLI-FOUNDATION.md |
| Provides    | `ledger account add`, `ledger account get`, `ledger account rename`, `ledger account delete` |
| Consumes    | accounts repository, transactions repository |

## Purpose

Manage account records through the CLI while preserving validation, uniqueness, transaction references, and the declared exit-code contract.

## Behavior

- `account add` validates the code and name, rejects duplicates, persists the account, and returns the account row.
- `account get` returns the requested account row or exits `4` when absent.
- `account rename` validates and persists the replacement name or exits `4` when absent.
- `account delete` removes an account with no transactions and returns `deleted` plus the code.
- Deletion of an account with transactions is rejected with exit `3`.
- Rejected operations produce no standard output and do not modify state.

## Programmatic Acceptance

=== AC account-create-read-update-delete ===
Intent: Account creation, retrieval, renaming, and deletion round-trip through the public CLI.
from cli.testing import cli_runner
import csv
import io

account = "CASH9"
name = "Event Float"
renamed = "Event Cash Box"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0

code, stdout, stderr = cli_runner("account", "get", account)
assert code == 0
rows = list(csv.DictReader(io.StringIO(stdout)))
assert rows[0]["account"] == account
assert rows[0]["name"] == name

assert cli_runner("account", "rename", account, renamed)[0] == 0
code, stdout, stderr = cli_runner("account", "get", account)
assert code == 0
assert list(csv.DictReader(io.StringIO(stdout)))[0]["name"] == renamed

assert cli_runner("account", "delete", account)[0] == 0
assert cli_runner("account", "get", account)[0] == 4
=== END AC account-create-read-update-delete ===

=== AC account-rejection-contract ===
Intent: Duplicate, absent, and in-use account operations return their declared exit codes.
from cli.testing import cli_runner

account = "CASH9"
name = "Event Float"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", account, name)[0] == 0
code, stdout, stderr = cli_runner("account", "add", account, name)
assert code == 3
assert stdout == ""

code, stdout, stderr = cli_runner("account", "get", "MISSING")
assert code == 4
assert stdout == ""

code, stdout, stderr = cli_runner("account", "delete", "MISSING")
assert code == 4
assert stdout == ""
=== END AC account-rejection-contract ===

=== AC account-in-use-protection ===
Intent: An account referenced by a transaction cannot be deleted.
from cli.testing import cli_runner

account = "CASH9"
name = "Event Float"

assert cli_runner("init")[0] == 0
assert cli_runner("load", "accounts", "sources/seed_accounts.csv")[0] == 1
=== END AC account-in-use-protection ===

## User Acceptance

- None.

## Guardrails

- Account codes and names follow the shared validation rules.
- Account deletion must preserve transaction referential integrity.
- Missing account operations return exit code `4` without standard output.

## Database Interface

- `FEATURE-ACCOUNT-001` — read: accounts.list - supplies: `—` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — write: accounts.create - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-003` — read: accounts.get - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-004` — write: accounts.update - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-005` — write: accounts.delete - supplies: `account` - returns: `account`
