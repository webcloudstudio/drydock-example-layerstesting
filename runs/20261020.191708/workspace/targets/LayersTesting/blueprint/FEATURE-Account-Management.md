# FEATURE: Account Management

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Add, retrieve, rename, and delete ledger accounts. |
| Depends On  | FEATURE-Account-Category-Loading.md, FEATURE-Transaction-Loading.md |
| Provides    | account add, account get, account rename, account delete |
| Consumes    | command dispatch, database configuration, accounts.create, accounts.get, accounts.update, accounts.delete |

## Purpose

Manage account master records while reporting transaction counts and integer-cent balances.

## Operations

- `account add <code> <name>` validates and creates an unused account.
- `account get <code>` returns the account balance row.
- `account rename <code> <name>` changes only the name.
- `account delete <code>` removes an account only when it has no transactions.

## Database Interface


- `FEATURE-DB-005` — read-write: accounts.get - supplies: `account` - returns: `account`, `name`, `transactions`, `balance`

## Programmatic Acceptance

=== AC account-crud-roundtrip ===
Intent: Account creation, retrieval, rename, and deletion persist through the public CLI.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    code, out, _ = cli_runner("account", "get", "A1")
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1][0:2] == ["A1", "Drawer"]
    assert cli_runner("account", "rename", "A1", "Front")[0] == 0
    code, out, _ = cli_runner("account", "get", "A1")
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1][1] == "Front"
    assert cli_runner("account", "delete", "A1")[0] == 0
    assert cli_runner("account", "get", "A1")[0] == 4
=== END AC account-crud-roundtrip ===

=== AC account-rejection-contract ===
Intent: Duplicate, invalid, absent, and in-use account operations return their specified statuses.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("account", "add", "A1", "Again")[0] == 3
    assert cli_runner("account", "get", "NOPE")[0] == 4
    assert cli_runner("account", "rename", "NOPE", "Name")[0] == 4
    assert cli_runner("account", "delete", "NOPE")[0] == 4
    assert cli_runner("account", "add", "CASH9", "Event Float")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
=== END AC account-rejection-contract ===

=== AC account-in-use-protection ===
Intent: An account with a transaction cannot be deleted.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A1", "Drawer")[0] == 0
    assert cli_runner("account", "add", "A2", "Other")[0] == 0
    assert cli_runner("category", "add", "C1", "Sales")[0] in (0, 2, 3)
    assert cli_runner("txn", "post", "A1", "C1", "1.00", "2026-01-01")[0] == 0
    assert cli_runner("account", "delete", "A1")[0] == 3
=== END AC account-in-use-protection ===

## User Acceptance

- None.

## Guardrails

- Account codes and names follow the source validation limits.
- Account deletion never cascades transactions.
- Failed operations preserve existing rows.
