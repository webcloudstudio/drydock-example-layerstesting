# FEATURE: Bulk Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Load validated account, category, and transaction CSV files atomically. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-SCHEMA-LIFECYCLE.md |
| Provides    | `ledger load accounts`, `ledger load categories`, `ledger load transactions` |
| Consumes    | accounts repository, categories repository, transactions repository |

## Behavior

`ledger load <table> <csv>` accepts only the declared table names and exact headers:

- accounts: `account,name`
- categories: `category,description`
- transactions: `txn_id,date,account,category,amount,memo`

The loader validates every row before writing:

- codes are one to twelve uppercase alphanumeric characters;
- names and descriptions are one to forty characters;
- memos are zero to sixty characters;
- amounts are decimal input with at most two fractional digits and are converted to integer cents;
- dates are real `YYYY-MM-DD` calendar dates;
- keys are unique;
- transaction references exist;
- the resulting balance of every account is non-negative.

A successful load reports the table and loaded row count. Any rejected load returns exit code `3` and leaves the target table unchanged.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-ACCOUNT-LIFECYCLE.md, FEATURE-TRANSACTION-LIFECYCLE.md.

## Programmatic Acceptance

=== AC bulk-load-valid-accounts ===
Intent: A valid account CSV loads successfully and reports the supplied row count.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    path = os.path.join(directory, "accounts.csv")
    rows = [["account", "name"], ["A1", "Main"], ["A2", "Reserve"]]
    with open(path, "w", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)
    try:
        assert cli_runner("init")[0] == 0
        code, output, error = cli_runner("load", "accounts", path)
        assert code == 0
        loaded = list(csv.reader(output.splitlines()))
        assert loaded[-1][1] == str(len(rows) - 1)
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC bulk-load-valid-accounts ===

=== AC bulk-load-invalid-row-is-atomic ===
Intent: A malformed row rejects the complete account file without storing earlier valid rows.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    path = os.path.join(directory, "accounts.csv")
    rows = [["account", "name"], ["A1", "Main"], ["bad-code!", "Invalid"]]
    with open(path, "w", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)
    try:
        assert cli_runner("init")[0] == 0
        code, output, error = cli_runner("load", "accounts", path)
        assert code == 3
        assert output == ""
        count_code, count_output, count_error = cli_runner("count")
        assert count_code == 0
        counts = list(csv.reader(count_output.splitlines()))
        assert counts[1][1] == "0"
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC bulk-load-invalid-row-is-atomic ===

=== AC bulk-load-unknown-reference-is-atomic ===
Intent: A transaction file with an unknown account is rejected before any transaction is written.

import csv
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = os.path.join(directory, "ledger.db")
    os.environ.pop("DATABASE_URL", None)
    account_path = os.path.join(directory, "accounts.csv")
    category_path = os.path.join(directory, "categories.csv")
    transaction_path = os.path.join(directory, "transactions.csv")
    for path, rows in (
        (account_path, [["account", "name"], ["A1", "Main"]]),
        (category_path, [["category", "description"], ["SALES", "Sales"]]),
        (transaction_path, [
            ["txn_id", "date", "account", "category", "amount", "memo"],
            ["1", "2026-01-01", "NOSUCH", "SALES", "1.00", "bad"],
        ]),
    ):
        with open(path, "w", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)
    try:
        assert cli_runner("init")[0] == 0
        assert cli_runner("load", "accounts", account_path)[0] == 0
        assert cli_runner("load", "categories", category_path)[0] == 0
        code, output, error = cli_runner("load", "transactions", transaction_path)
        assert code == 3
        assert output == ""
        count_code, count_output, count_error = cli_runner("count")
        assert count_code == 0
        counts = list(csv.reader(count_output.splitlines()))
        assert counts[3][1] == "0"
    finally:
        if old is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = old
=== END AC bulk-load-unknown-reference-is-atomic ===

## User Acceptance

- None.

## Guardrails

- Loading must validate the entire file before its first write.
- Failed loads must not partially modify any table.
- The loader must not read or modify files under `sources/` from application code.
- Amounts must be converted to integer cents without floating-point arithmetic.
