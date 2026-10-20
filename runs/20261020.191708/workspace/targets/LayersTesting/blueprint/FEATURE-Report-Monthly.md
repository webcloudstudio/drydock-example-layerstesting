# FEATURE: Monthly Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Report transaction totals grouped by calendar month. |
| Depends On  | FEATURE-Transaction-Management.md |
| Provides    | report monthly |
| Consumes    | transactions.list |

## Purpose

The monthly report groups transactions by their `YYYY-MM` calendar month, orders months ascending, and appends a computed total row.

## Workflow

Query transactions, derive each month from the validated date, calculate counts and flow totals in integer cents, order months ascending, format amounts with two decimals, and emit the total.

## Programmatic Acceptance

=== AC monthly-report-groups-months ===
Intent: The monthly report groups persisted transactions by ascending calendar month.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A", "Account")[0] == 0
    assert cli_runner("category", "add", "C", "Category")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "2.00", "later")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "3.50", "earlier")[0] == 0

    code, output, _ = cli_runner("report", "monthly")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    months = [row[0] for row in rows[1:-1]]
    assert months == ["2026-01"]

    assert rows[1][1:] == ["2", "5.50", "0.00", "5.50"]

=== END AC monthly-report-groups-months ===

=== AC monthly-report-separates-months ===
Intent: Transactions in separate months produce separate monthly rows and a computed total.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("account", "add", "A", "Account")[0] == 0
    assert cli_runner("category", "add", "C", "Category")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "2.00", "jan")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "-1.25", "feb")[0] == 0

    code, output, _ = cli_runner("report", "monthly")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    assert len(rows) == 4
    assert rows[-1][1:] == ["2", "2.00", "1.25", "0.75"]

=== END AC monthly-report-separates-months ===

=== AC monthly-report-empty ===
Intent: An initialized empty ledger produces only the monthly header and total row.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    code, output, _ = cli_runner("report", "monthly")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    assert len(rows) == 2
    assert rows[-1][0] == "TOTAL"

=== END AC monthly-report-empty ===

## User Acceptance

- None.

## Guardrails

- Months are ordered ascending.
- Monthly totals are derived from persisted transactions.
- Money calculations use integer cents.
