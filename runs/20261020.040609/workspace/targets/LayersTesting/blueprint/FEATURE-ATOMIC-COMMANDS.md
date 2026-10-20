# FEATURE: Atomic Commands

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Every ledger command runs as one database transaction that commits in full or changes nothing. |
| Depends On  | DATABASE.md, FEATURE-LEDGER-ENTRY.md, FEATURE-SCHEMA-INIT.md, FEATURE-DATABASE-SELECTION.md, FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |

## Purpose

Wraps every command handler in a single transaction through the generated persistence layer. A
command that fails for any reason rolls back, leaving every table as it was. A transfer stores both
of its rows or neither. Concurrent commands each commit or fail as a single unit.

Writer serialization follows the persistence library's default transaction behavior (decision
Q-002). No application-level retry loop is added.

## Database Interface

- `FEATURE-TXN-001` — write: create a transaction in the same transaction as the command - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-005` — write: delete a transaction within the command's transaction - supplies: `txn_id` - returns: `deleted`

## Programmatic Acceptance

=== AC atomic-rejected-post-changes-nothing ===
Intent: A post rejected for an unknown account leaves every table exactly as it was.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
before = cli_runner("count")[1]
code, out, err = cli_runner("txn", "post", "NOSUCH", "SALES", "1.00", "2026-01-02")
assert code == 3
assert cli_runner("txn", "get", "1")[0] == 4
assert cli_runner("count")[1] == before
=== END AC atomic-rejected-post-changes-nothing ===

=== AC atomic-rejected-transfer-changes-nothing ===
Intent: A transfer rejected for identical accounts, a non-positive amount, or an unknown account stores neither row.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("account", "add", "CASH2", "Second Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
before = cli_runner("count")[1]
assert cli_runner("transfer", "CASH1", "CASH1", "5.00", "2026-01-02")[0] == 3
assert cli_runner("transfer", "CASH1", "CASH2", "-1.00", "2026-01-02")[0] == 3
assert cli_runner("transfer", "CASH1", "NOSUCH", "5.00", "2026-01-02")[0] == 3
assert cli_runner("count")[1] == before
assert cli_runner("txn", "get", "1")[0] == 4
=== END AC atomic-rejected-transfer-changes-nothing ===

=== AC atomic-transfer-stores-both-rows ===
Intent: A successful transfer stores exactly its two legs under consecutive ids, outgoing first.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")

legs = 2
first_id = 2
amount_text = "5.00"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("account", "add", "CASH2", "Second Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
assert cli_runner("txn", "post", "CASH1", "SALES", "10.00", "2026-01-01")[0] == 0

code, out, err = cli_runner("transfer", "CASH1", "CASH2", amount_text, "2026-01-02")
assert code == 0
rows = out.splitlines()[1:]
assert len(rows) == legs
ids = [row.split(",")[0] for row in rows]
assert ids == [str(first_id), str(first_id + 1)]
assert cli_runner("txn", "get", str(first_id))[0] == 0
assert cli_runner("txn", "get", str(first_id + 1))[0] == 0
=== END AC atomic-transfer-stores-both-rows ===

=== AC atomic-concurrent-commands ===
Intent: Two or more concurrent ledger processes each commit or fail as a single unit, so the stored row count equals the number of successful exits.

import os
import subprocess
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
database = os.path.join(work, "ledger.db")
os.environ["DATABASE_URL"] = database
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0

env = {**os.environ, "DATABASE_URL": database}
ledger = os.path.join(os.getcwd(), "ledger")
attempts = 4
procs = [
    subprocess.Popen(
        [ledger, "txn", "post", "CASH1", "SALES", "1.00", "2026-01-02"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    )
    for _ in range(attempts)
]
results = [proc.communicate() for proc in procs]
codes = [proc.returncode for proc in procs]
for (out, err), code in zip(results, codes):
    print(code, err)

assert all(code in (0, 1, 3) for code in codes)
transaction_rows = int(cli_runner("count")[1].splitlines()[3].split(",")[1])
assert transaction_rows == codes.count(0)
=== END AC atomic-concurrent-commands ===

## User Acceptance

- None.

## Guardrails

- No command handler opens a database driver directly; every write goes through `db.<table>.<verb>(...)`.
- A command never commits a partial result, including on an exception path.
- Writes are never retried by application code to mask a conflict.
