# FEATURE: Account Transfers

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Execute atomic two-row transfers between ledger accounts. |
| Depends On  | FEATURE-Balance-Invariant.md, FEATURE-Transaction-Management.md |
| Provides    | transfer |
| Consumes    | command dispatch, transactions.create, accounts.get, categories.get, prospective balance validation |

## Purpose

A transfer moves a positive amount from one existing account to another by creating two consecutive transactions in category `TRANSFER`.

## Workflow

1. Validate both account codes, account existence, distinctness, positive amount, date, and the `TRANSFER` category.
2. Calculate both prospective balances before writing.
3. Create the outgoing row, then the incoming row, in one transaction.
4. Emit both transaction rows in identifier order.
5. Roll back completely on any rejection.

The outgoing memo is `transfer to <destination>` and the incoming memo is `transfer from <source>`.

## Programmatic Acceptance

=== AC transfers-success ===
Intent: A valid transfer creates two persisted transaction rows and succeeds.
from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    dsn = os.path.join(directory, "ledger.db")
    os.environ["DATABASE_URL"] = dsn

    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "FROM", "Source")[0] == 0
    assert cli_runner("account", "add", "TO", "Destination")[0] == 0
    assert cli_runner("category", "add", "TRANSFER", "Internal transfer")[0] == 0
    assert cli_runner("txn", "post", "FROM", "TRANSFER", "100.00", "2026-04-01")[0] == 0

    code, output, _ = cli_runner("transfer", "FROM", "TO", "25.00", "2026-04-02")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    assert len(rows) == 3

    with db_session(dsn) as db:
        transactions = db.transactions.list()
        assert len(transactions) == 3
        assert transactions[-2].amount == -2500
        assert transactions[-1].amount == 2500
        assert transactions[-2].account == "FROM"
        assert transactions[-1].account == "TO"
=== END AC transfers-success ===

=== AC transfers-rejects-insufficient-balance ===
Intent: An insufficient-balance transfer is rejected without changing transactions.
from cli.testing import cli_runner
from persistence.testing import db_session
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    dsn = os.path.join(directory, "ledger.db")
    os.environ["DATABASE_URL"] = dsn

    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "FROM", "Source")[0] == 0
    assert cli_runner("account", "add", "TO", "Destination")[0] == 0
    assert cli_runner("category", "add", "TRANSFER", "Internal transfer")[0] == 0
    assert cli_runner("txn", "post", "FROM", "TRANSFER", "10.00", "2026-04-01")[0] == 0

    code, _, _ = cli_runner("transfer", "FROM", "TO", "11.00", "2026-04-02")
    assert code == 3

    with db_session(dsn) as db:
        transactions = db.transactions.list()
        assert len(transactions) == 1
=== END AC transfers-rejects-insufficient-balance ===

=== AC transfers-rejects-invalid-accounts ===
Intent: Transfers reject equal or unknown account codes before writing.
from cli.testing import cli_runner
from persistence.testing import db_session
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    dsn = os.path.join(directory, "ledger.db")
    os.environ["DATABASE_URL"] = dsn

    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "FROM", "Source")[0] == 0
    assert cli_runner("category", "add", "TRANSFER", "Internal transfer")[0] == 0

    assert cli_runner("transfer", "FROM", "FROM", "1.00", "2026-04-01")[0] == 3
    assert cli_runner("transfer", "FROM", "MISSING", "1.00", "2026-04-01")[0] == 3

    with db_session(dsn) as db:
        assert len(db.transactions.list()) == 0
=== END AC transfers-rejects-invalid-accounts ===

## User Acceptance

- None.

## Guardrails

- Transfers create both rows or neither row.
- Transfer amounts are positive input values.
- No transfer may leave an account balance negative.
- Application code accesses persistence only through the shipped library.
