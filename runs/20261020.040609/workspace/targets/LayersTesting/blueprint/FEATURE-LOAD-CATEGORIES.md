# FEATURE: Load Categories

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads categories from a CSV file, validating every row before commit. |
| Depends On  | FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-CODE.md, FEATURE-VALIDATE-TEXT.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md, DATABASE.md |
| Provides    | ledger load categories <csv> |

## Purpose

`ledger load categories <csv>` reads a file whose header is `category,description`, validates each
row's code and description, and inserts every row in one transaction. Output is `table,loaded` then
`categories,<rows>`. A row that fails validation or duplicates an existing key rejects the whole
file with exit 3.

## Database Interface

- `FEATURE-CATEGORY-001` — write: create a category from a loaded row - supplies: `category`, `description` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-categories-valid-file ===
Intent: A valid categories file loads every row and writes table,loaded then categories,<rows>.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\nRENT,Rent\n")
row_count = 2

assert cli_runner("init")[0] == 0
code, out, err = cli_runner("load", "categories", categories)
assert code == 0
lines = out.splitlines()
assert lines[0] == "table,loaded"
assert lines[1].split(",") == ["categories", str(row_count)]
assert cli_runner("count")[1].splitlines()[2].split(",") == ["categories", str(row_count)]
=== END AC load-categories-valid-file ===

=== AC load-categories-usable-by-posting ===
Intent: A loaded category code is accepted by txn post and reads back on the stored transaction.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")
category_code = "SALES"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
assert cli_runner("txn", "post", "CASH1", category_code, "10.00", "2026-01-01")[0] == 0
row = cli_runner("txn", "get", "1")[1].splitlines()[1].split(",")
assert row[3] == category_code
=== END AC load-categories-usable-by-posting ===

=== AC load-categories-invalid-row-rejects-file ===
Intent: A file containing an invalid category code exits 3 and stores none of its rows.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\nSALE$,Bad Code\n")
empty = 0

assert cli_runner("init")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 3
rows = int(cli_runner("count")[1].splitlines()[2].split(",")[1])
assert rows == empty
=== END AC load-categories-invalid-row-rejects-file ===

=== AC load-categories-duplicate-key-rejected ===
Intent: Loading a category code that already exists exits 3 and leaves the stored count unchanged.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")

assert cli_runner("init")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
before = cli_runner("count")[1]
assert cli_runner("load", "categories", categories)[0] == 3
assert cli_runner("count")[1] == before
=== END AC load-categories-duplicate-key-rejected ===

## User Acceptance

- None.

## Guardrails

- The loader reads the file only through the `categories` table operations; it never opens a driver.
- Validation of every row completes before the transaction commits.
