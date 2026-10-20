# FEATURE: Account and Category Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Atomically validate and load account and category CSV files. |
| Depends On  | ARCHITECTURE.md, FEATURE-CLI-Dispatcher.md, FEATURE-CLI-Validation.md, FEATURE-Database-Configuration.md |
| Provides    | load accounts, load categories |
| Consumes    | command dispatch, database configuration, accounts.create, categories.create |

## Purpose

`ledger load accounts <csv>` and `ledger load categories <csv>` import validated master data. Files must be readable, have the exact table header, contain valid codes and text, and contain no duplicate keys. Validation completes before any row is written.

## Workflow

1. Resolve the configured database.
2. Read and validate the complete file.
3. Reject malformed rows, duplicate keys, or conflicts with existing rows without changing state.
4. Insert all rows atomically.
5. Emit the loaded table and count.

## Database Interface

- `FEATURE-DB-002` — read-write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-DB-003` — read-write: create a category - supplies: `category`, `description` - returns: `category`, `description`

## Programmatic Acceptance

=== AC account-category-load-roundtrip ===
Intent: Valid account and category files are loaded and their persisted rows are readable.
import csv
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    accounts = Path(d) / "accounts.csv"
    categories = Path(d) / "categories.csv"
    account_rows = [["account", "name"], ["A1", "Drawer"]]
    category_rows = [["category", "description"], ["C1", "Sales"]]
    accounts.write_text("\n".join(",".join(r) for r in account_rows) + "\n")
    categories.write_text("\n".join(",".join(r) for r in category_rows) + "\n")
    assert cli_runner("load", "accounts", str(accounts))[0] == 0
    assert cli_runner("load", "categories", str(categories))[0] == 0
    code, out, _ = cli_runner("account", "get", "A1")
    assert code == 0
    assert list(csv.reader(out.splitlines()))[1][0:2] == account_rows[1]
=== END AC account-category-load-roundtrip ===

=== AC account-category-load-rejects-without-write ===
Intent: An unreadable or invalid master-data file is rejected without changing persisted data.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    path = Path(d) / "bad.csv"
    path.write_text("wrong,header\nA1,Drawer\n")
    before = cli_runner("count")
    assert before[0] == 0
    assert cli_runner("load", "accounts", str(path))[0] == 3
    after = cli_runner("count")
    assert after[0] == 0
    assert after[1] == before[1]
    assert cli_runner("load", "accounts", str(Path(d) / "missing.csv"))[0] == 1
=== END AC account-category-load-rejects-without-write ===

=== AC account-category-load-validation ===
Intent: Duplicate and invalid master-data fields return the rejected-command status.
import os
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    os.environ["DATABASE_PATH"] = str(Path(d) / "ledger.db")
    assert cli_runner("init")[0] == 0
    duplicate = Path(d) / "duplicate.csv"
    duplicate.write_text("account,name\nA1,One\nA1,Two\n")
    assert cli_runner("load", "accounts", str(duplicate))[0] == 3
    invalid = Path(d) / "invalid.csv"
    invalid.write_text("category,description\nbad-code,Sales\n")
    assert cli_runner("load", "categories", str(invalid))[0] == 3
=== END AC account-category-load-validation ===

## User Acceptance

- None.

## Guardrails

- A rejected load writes no rows.
- Application code uses only the shipped persistence library.
- Imported files are never modified.
