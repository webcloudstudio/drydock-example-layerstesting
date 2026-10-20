# FEATURE: Schema Count

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Implements `ledger count`, which prints the row count of each ledger table. |
| Depends On  | FEATURE-Schema-Init.md, FEATURE-CLI-Output.md, DATABASE.md |
| Provides    | ledger count |
| Consumes    | open_database, write_csv |

## Purpose

`ledger count` tells an operator how many rows each table holds, which is how the seed loads are checked.

## Behavior

- Prints `table,rows`, then one line each for `accounts`, `categories`, and `transactions`, in that order.
- Each count is the number of rows returned by that table's list operation in `DATABASE.md`. No count is stored or hardcoded.
- The output is written through `write_csv`, so the contract in FEATURE-CLI-Output.md applies.
- Exits 0 on success.

## Programmatic Acceptance

=== AC schema-count-header-and-order ===
Intent: `ledger count` writes a `table,rows` header followed by the three table lines in the fixed order.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

init_code, init_out, init_err = cli_runner("init")
assert init_code == 0

code, out, err = cli_runner("count")
assert code == 0
lines = out.splitlines()
assert len(lines) == 4
assert lines[0].split(",") == ["table", "rows"]
assert [line.split(",")[0] for line in lines[1:]] == ["accounts", "categories", "transactions"]
=== END AC schema-count-header-and-order ===

=== AC schema-count-matches-stored-rows ===
Intent: Each count equals the number of rows the store holds for that table after known inserts.

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

init_code, init_out, init_err = cli_runner("init")
assert init_code == 0

db = open_database(dsn)
db.accounts.create(account="CNTA1", name="Count Account One")
db.accounts.create(account="CNTA2", name="Count Account Two")
db.categories.create(category="CNTC1", description="Count Category")
db.transactions.create(txn_id=1, date="2026-01-05", account="CNTA1", category="CNTC1", amount=1250, memo="count test")

expected = {"accounts": 2, "categories": 1, "transactions": 1}

code, out, err = cli_runner("count")
assert code == 0
counts = {line.split(",")[0]: int(line.split(",")[1]) for line in out.splitlines()[1:]}
assert counts == expected
=== END AC schema-count-matches-stored-rows ===

=== AC schema-count-zero-after-init ===
Intent: On a freshly initialized store, every table count is zero.

import os
import tempfile

from cli.testing import cli_runner

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn

init_code, init_out, init_err = cli_runner("init")
assert init_code == 0

code, out, err = cli_runner("count")
assert code == 0
rows = [line.split(",") for line in out.splitlines()[1:]]
assert len(rows) == 3
assert all(int(row[1]) == 0 for row in rows)
=== END AC schema-count-zero-after-init ===

## User Acceptance

- None.

## Guardrails

- No count value is hardcoded in this handler; every count comes from a query.
- `count` takes no arguments and does not modify any table.
