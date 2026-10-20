# FEATURE: Financial Invariants

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Enforce atomic rejected mutations and non-negative account balances across ledger operations. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-BULK-LOADING.md, FEATURE-TRANSACTION-LIFECYCLE.md, FEATURE-TRANSFERS.md |
| Provides    | cross-command balance invariant enforcement |
| Consumes    | accounts repository, transactions repository |

## Purpose

Every load, post, amend, delete, and transfer validates the complete resulting ledger before its first write. Rejected operations return exit code 3, produce no standard output, and preserve all existing rows. No account may have a negative balance.

## Invariants

- Balances are calculated as the sum of integer-cent transaction amounts per account.
- Validation includes all affected accounts and all existing transactions.
- A rejected operation is atomic and leaves the database unchanged.
- Financial validation uses integer cents only.

## Programmatic Acceptance

=== AC financial-rejects-negative-post ===
Intent: A transaction that would make an account negative is rejected without creating a transaction.
Requires: python-package=pytest; scope=test

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as directory:
    database_path = os.path.join(directory, "ledger.db")
    previous = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = database_path
    try:
        init_code, _, _ = cli_runner("init")
        assert init_code == 0

        with open_database(database_path) as db:
            db.accounts.create(account="CASH", name="Cash")
            db.categories.create(category="SALES", description="Sales")

        amount = "-1.00"
        code, _, _ = cli_runner("txn", "post", "CASH", "SALES", amount, "2026-01-01")
        assert code == 3

        with open_database(database_path) as db:
            rows = list(db.transactions.list())
            assert rows == []
    finally:
        if previous is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = previous
=== END AC financial-rejects-negative-post ===

=== AC financial-rejects-transfer-without-balance ===
Intent: A transfer that would overdraw its source account creates neither transaction row.
Requires: python-package=pytest; scope=test

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as directory:
    database_path = os.path.join(directory, "ledger.db")
    previous = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = database_path
    try:
        init_code, _, _ = cli_runner("init")
        assert init_code == 0

        with open_database(database_path) as db:
            db.accounts.create(account="FROM", name="From")
            db.accounts.create(account="TO", name="To")
            db.categories.create(category="TRANSFER", description="Transfer")

        amount = "1.00"
        code, _, _ = cli_runner("transfer", "FROM", "TO", amount, "2026-01-01")
        assert code == 3

        with open_database(database_path) as db:
            rows = list(db.transactions.list())
            assert rows == []
    finally:
        if previous is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = previous
=== END AC financial-rejects-transfer-without-balance ===

=== AC financial-rejects-invalid-amendment ===
Intent: An amendment that would make an account negative is rejected and preserves the original transaction.
Requires: python-package=pytest; scope=test

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

with tempfile.TemporaryDirectory() as directory:
    database_path = os.path.join(directory, "ledger.db")
    previous = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = database_path
    try:
        init_code, _, _ = cli_runner("init")
        assert init_code == 0

        with open_database(database_path) as db:
            db.accounts.create(account="CASH", name="Cash")
            db.categories.create(category="SALES", description="Sales")

        original_amount = "10.00"
        post_code, _, _ = cli_runner(
            "txn", "post", "CASH", "SALES", original_amount, "2026-01-01"
        )
        assert post_code == 0

        replacement_amount = "-20.00"
        amend_code, _, _ = cli_runner("txn", "amend", "1", replacement_amount)
        assert amend_code == 3

        with open_database(database_path) as db:
            row = db.transactions.get(txn_id=1)
            assert row.amount == 1000
    finally:
        if previous is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = previous
=== END AC financial-rejects-invalid-amendment ===

## User Acceptance

- None.

## Guardrails

- No rejected mutation may write partial state.
- No account balance may become negative.
- Application code must use the shipped persistence package and integer cents.
