# FEATURE: Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provides account creation, retrieval, renaming, and deletion through the CLI. |
| Depends On  | DATABASE.md, FEATURE-Validation.md, FEATURE-Bulk-Reference-Loading.md |
| Provides    | `ledger account add`, `ledger account get`, `ledger account rename`, `ledger account delete` |
| Consumes    | domain validation, relational ledger schema, account persistence operations |

## Purpose

Manage account records while deriving transaction counts and balances from persisted transactions.

## Workflows

- `account add` creates a unique validated account.
- `account get` returns an existing account row.
- `account rename` changes only the account name.
- `account delete` removes an account only when it has no transactions.

Missing accounts return exit code `4`; rejected changes return exit code `3`.

## Database Interface

- `FEATURE-LEDGER-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-LEDGER-002` — read: retrieve an account - supplies: `account` - returns: `account`, `name`
- `FEATURE-LEDGER-003` — write: update an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-LEDGER-004` — write: delete an account - supplies: `account` - returns: `deleted`

## Programmatic Acceptance

=== AC accounts-create-read ===
Intent: An added account can be read back with its initial aggregate values.
from cli.testing import cli_runner

code, stdout, stderr = cli_runner("account", "add", "A", "Alpha")
assert code == 0
get_code, get_stdout, get_stderr = cli_runner("account", "get", "A")
assert get_code == 0
assert "A,Alpha,0,0.00" in get_stdout
=== END AC accounts-create-read ===

=== AC accounts-rename ===
Intent: Renaming an account changes its persisted name.
from cli.testing import cli_runner

add_code, _, _ = cli_runner("account", "add", "A", "Alpha")
assert add_code == 0
code, stdout, stderr = cli_runner("account", "rename", "A", "Beta")
assert code == 0
get_code, get_stdout, get_stderr = cli_runner("account", "get", "A")
assert get_code == 0
assert "A,Beta,0,0.00" in get_stdout
=== END AC accounts-rename ===

=== AC accounts-delete-and-not-found ===
Intent: An unused account can be deleted and is subsequently absent.
from cli.testing import cli_runner

add_code, _, _ = cli_runner("account", "add", "A", "Alpha")
assert add_code == 0
delete_code, stdout, stderr = cli_runner("account", "delete", "A")
assert delete_code == 0
missing_code, missing_stdout, missing_stderr = cli_runner("account", "get", "A")
assert missing_code == 4
assert missing_stdout == ""
=== END AC accounts-delete-and-not-found ===

=== AC accounts-in-use-rejected ===
Intent: An account referenced by a transaction cannot be deleted.
from cli.testing import cli_runner

account_code, _, _ = cli_runner("account", "add", "A", "Alpha")
category_code, _, _ = cli_runner("load", "categories", "sources/seed_categories.csv")
assert account_code == 0
assert category_code == 0
post_code, _, _ = cli_runner("txn", "post", "A", "SALES", "1.00", "2026-01-01")
assert post_code == 0
delete_code, delete_stdout, delete_stderr = cli_runner("account", "delete", "A")
assert delete_code == 3
assert delete_stdout == ""
=== END AC accounts-in-use-rejected ===

## User Acceptance

- None.

## Guardrails

- Account codes and names obey the shared validation rules.
- Account balances and transaction counts are query-derived.
- Failed account operations write no output to standard output and change no data.
