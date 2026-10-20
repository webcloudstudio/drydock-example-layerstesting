# FEATURE: Category Report

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Report transaction totals grouped by category. |
| Depends On  | FEATURE-Transaction-Management.md |
| Provides    | report categories |
| Consumes    | categories.list, transactions.list |

## Purpose

The category report includes every category, including categories without transactions, and reports transaction count, inflow, outflow, and net totals.

## Workflow

Query categories and transactions, group transactions by category code, calculate positive inflow and absolute negative outflow in cents, include zero-activity categories, order by code, and append a computed total row.

## Programmatic Acceptance

=== AC category-report-includes-zero-activity ===
Intent: The category report includes categories with no transactions.
from cli.testing import cli_runner
import csv
import io
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    assert cli_runner("init")[0] == 0
    assert cli_runner("category", "add", "ACTIVE", "Active")[0] == 0
    assert cli_runner("category", "add", "EMPTY", "Empty")[0] == 0
    assert cli_runner("account", "add", "A", "Account")[0] == 0
    assert cli_runner("txn", "post", "A", "ACTIVE", "5.00", "receipt")[0] == 0

    code, output, _ = cli_runner("report", "categories")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    category_codes = [row[0] for row in rows[1:-1]]
    assert category_codes == ["ACTIVE", "EMPTY"]
    empty = rows[2]
    assert empty[2:] == ["0", "0.00", "0.00", "0.00"]

=== END AC category-report-includes-zero-activity ===

=== AC category-report-calculates-flows ===
Intent: The category report calculates inflow, outflow, and net from persisted integer cents.
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
    assert cli_runner("txn", "post", "A", "C", "10.00", "in")[0] == 0
    assert cli_runner("txn", "post", "A", "C", "-3.25", "out")[0] == 0

    code, output, _ = cli_runner("report", "categories")
    assert code == 0
    rows = list(csv.reader(io.StringIO(output)))
    category = rows[1]
    total = rows[-1]
    assert category[2:] == ["2", "10.00", "3.25", "6.75"]
    assert total[1:] == ["", "2", "10.00", "3.25", "6.75"]

=== END AC category-report-calculates-flows ===

=== AC category-report-rejects-unknown-report ===
Intent: An unknown category report name returns a usage error without output.
from cli.testing import cli_runner
import os
import tempfile

with tempfile.TemporaryDirectory() as directory:
    os.environ["DATABASE_URL"] = os.path.join(directory, "ledger.db")
    code, output, _ = cli_runner("report", "unknown")
    assert code == 2
    assert output == ""

=== END AC category-report-rejects-unknown-report ===

## User Acceptance

- None.

## Guardrails

- Zero-activity categories are included.
- Outflow is reported as a positive amount.
- Totals are computed from persisted rows.
