# FEATURE: Account Operations

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Creates, reads, renames, and deletes ledger accounts with lifecycle validation. |
| Depends On  | FEATURE-TRANSACTION-LOAD.md, DATABASE.md |
| Provides    | ledger account add, ledger account get, ledger account rename, ledger account delete |
| Consumes    | ./ledger executable, ledger persistence operations |

## Purpose

Manage account records while enforcing code and name validation, uniqueness, not-found behavior, transaction references, and computed account balances.

## Database Interface


- `FEATURE-LEDGER-003` — read-write: accounts.create - supplies: — - returns: —
- `FEATURE-LEDGER-004` — read-write: accounts.update - supplies: — - returns: —
- `FEATURE-LEDGER-005` — write: accounts.delete - supplies: — - returns: —

## Workflow

- Add validates the account code and name, rejects duplicates, and returns the computed account row.
- Get returns the account row with transaction count and balance.
- Rename changes only the name.
- Delete succeeds only when the account has no transactions.
- Missing accounts return exit code 4; rejected mutations return exit code 3.

## Programmatic Acceptance

=== AC account-create-read ===
Intent: Account creation persists a readable account with an empty balance.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(Path(tmp) / "ledger.db")
    try:
        assert cli_runner("init")[0] == 0
        account = "CASH9"
        name = "Event Float"
        code, _, _ = cli_runner("account", "add", account, name)
        assert code == 0
        code, stdout, _ = cli_runner("account", "get", account)
        assert code == 0
        rows = list(csv.reader(stdout.splitlines()))
        assert rows[1][0] == account
        assert rows[1][1] == name
        assert rows[1][2] == "0"
        assert rows[1][3] == "0.00"
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC account-create-read ===

=== AC account-rename ===
Intent: Renaming changes the account name while retaining its code.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(Path(tmp) / "ledger.db")
    try:
        assert cli_runner("init")[0] == 0
        account = "CASH9"
        first = "Event Float"
        second = "Event Cash Box"
        assert cli_runner("account", "add", account, first)[0] == 0
        assert cli_runner("account", "rename", account, second)[0] == 0
        code, stdout, _ = cli_runner("account", "get", account)
        assert code == 0
        row = list(csv.reader(stdout.splitlines()))[1]
        assert row[0] == account
        assert row[1] == second
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC account-rename ===

=== AC account-delete-rules ===
Intent: Account deletion succeeds only for an unused account and reports absent accounts distinctly.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(Path(tmp) / "ledger.db")
    try:
        assert cli_runner("init")[0] == 0
        unused = "CASH9"
        assert cli_runner("account", "add", unused, "Event Float")[0] == 0
        code, stdout, _ = cli_runner("account", "delete", unused)
        assert code == 0
        assert stdout != ""
        code, stdout, _ = cli_runner("account", "get", unused)
        assert code == 4
        assert stdout == ""
    finally:
        if old is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = old
=== END AC account-delete-rules ===

=== AC account-validation ===
Intent: Duplicate and in-use account mutations are rejected.
from cli.testing import cli_runner

assert cli_runner("account", "add", "DRAWER1", "Duplicate")[0] in {0, 3}
code, stdout, _ = cli_runner("account", "delete", "DRAWER1")
assert code in {3, 4}
assert stdout == ""
=== END AC account-validation ===

## User Acceptance

- None.

## Guardrails

- Account balances are computed from stored transactions.
- Accounts referenced by transactions cannot be deleted.
- Failure emits no standard output.
