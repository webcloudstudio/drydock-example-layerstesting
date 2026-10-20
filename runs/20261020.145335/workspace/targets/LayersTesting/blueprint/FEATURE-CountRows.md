# FEATURE: Count Rows

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Provide `ledger count`, which reports the row count of each ledger table. |
| Depends On  | FEATURE-InitSchema.md, FEATURE-CliOutput.md, DATABASE.md |
| Provides    | ledger count |
| Consumes    | db.accounts.list, db.categories.list, db.transactions.list |

## Purpose

`ledger count` writes the row count of each ledger table as CSV. Each count is a query against the
store. No count is stored, cached, or hardcoded.

## Trigger

`ledger count` with no further arguments.

## Sequence

1. Resolve the database target and open the store.
2. Count rows in `accounts`, then `categories`, then `transactions`, each by a query.
3. Write the header and three rows, then exit `0`.

## Routes and Interfaces

- `ledger count`: writes `table,rows`, then `accounts,<n>`, `categories,<n>`, `transactions,<n>`.
- Exit `1` when the tables are missing, with nothing on standard output.

## Reads and Writes

- Reads: all rows of `accounts`, `categories`, and `transactions`, counted by query.
- Writes: none.

## Programmatic Acceptance

=== AC count-header-and-order ===
Intent: `ledger count` writes the header, then the accounts, categories, and transactions rows in that order, exit 0.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

expected_exit = 0
code, out, err = cli_runner("count")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
lines = out.splitlines()
assert lines[0] == "table,rows"
assert [line.split(",")[0] for line in lines[1:]] == ["accounts", "categories", "transactions"]
=== END AC count-header-and-order ===

=== AC count-matches-query ===
Intent: Each reported count equals the row count returned by the store's own query.
import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

db = open_database(os.environ["DATABASE_URL"])
db.accounts.create(account="CASH1", name="Till")
db.accounts.create(account="CASH2", name="Safe")

code, out, err = cli_runner("count")
print("stdout:", repr(out), "stderr:", repr(err))
counts = {line.split(",")[0]: line.split(",")[1] for line in out.splitlines()[1:]}
assert counts["accounts"] == str(len(db.accounts.list()))
assert counts["categories"] == str(len(db.categories.list()))
assert counts["transactions"] == str(len(db.transactions.list()))
=== END AC count-matches-query ===

=== AC count-after-init-is-zero ===
Intent: Immediately after `init`, every reported count is zero.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

code, out, err = cli_runner("count")
print("stdout:", repr(out), "stderr:", repr(err))
counts = [line.split(",")[1] for line in out.splitlines()[1:]]
assert counts == ["0", "0", "0"]
=== END AC count-after-init-is-zero ===

=== AC count-rejects-extra-argument ===
Intent: Extra arguments to `count` are a usage error with exit 2 and no stdout.
import os
import tempfile

from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
cli_runner("init")

expected_exit = 2
code, out, err = cli_runner("count", "extra")
print("stdout:", repr(out), "stderr:", repr(err))
assert code == expected_exit
assert out == ""
=== END AC count-rejects-extra-argument ===

## User Acceptance

- None.

## Guardrails

- Counts are never hardcoded; every number is a query result.
- Output contains no quoting and uses `\n` line endings.
