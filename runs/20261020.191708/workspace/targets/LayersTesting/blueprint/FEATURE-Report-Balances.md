# FEATURE: Balance Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Report account balances and transaction counts from persisted ledger data. |
| Depends On  | FEATURE-Transaction-Management.md |
| Provides    | report balances |
| Consumes    | accounts.list, transactions.list |

## Purpose

The balances report lists every account ordered by account code, with its transaction count and integer-cent balance, followed by a computed total row.

## Workflow

Query accounts and transactions through the persistence layer, calculate each account's count and sum, format cents with exactly two decimal places, and calculate totals from the queried rows.

## Programmatic Acceptance

=== AC balance-report-empty ===
Intent: The balances report succeeds for an initialized empty ledger and reports no account rows.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0

    code, output, _ = cli_runner("report", "balances")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    assert len(rows) == 2
    assert rows[-1][0] == "TOTAL"
    assert rows[-1][2] == "0"

=== END AC balance-report-empty ===

=== AC balance-report-computes-persisted-state ===
Intent: The report reflects persisted account counts and balances after transactions.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "B", "Second")[0] == 0
    assert cli_runner("account", "add", "A", "First")[0] == 0
    assert cli_runner("category", "add", "C", "Category")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "12.50", "2026-01-01")[0] == 0
    assert cli_runner("txn", "post", "B", "C", "3.25", "2026-01-02")[0] == 0

    code, output, _ = cli_runner("report", "balances")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    assert [row[0] for row in rows[1:-1]] == ["A", "B"]
    assert rows[1][2] == "1"
    assert rows[1][3] == "12.50"
    assert rows[-1][2] == "2"
    assert rows[-1][3] == "15.75"

=== END AC balance-report-computes-persisted-state ===

=== AC balance-report-missing-database ===
Intent: A balances report against an unavailable database path returns an operational failure.
from cli.testing import cli_runner
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "missing", "ledger.db")
    code, output, _ = cli_runner("report", "balances")
    assert code == 1
    assert output == ""

=== END AC balance-report-missing-database ===

## User Acceptance

- None.

## Guardrails

- Account rows are ordered by account code.
- Totals are computed from database rows, never hardcoded.
- Amounts are stored as integer cents and rendered with two decimals.
