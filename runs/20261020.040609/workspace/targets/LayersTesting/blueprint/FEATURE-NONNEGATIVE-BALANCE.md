# FEATURE: Non-Negative Balance

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Rejects any command that would leave an account balance below zero, checked before commit. |
| Depends On  | FEATURE-ATOMIC-COMMANDS.md, FEATURE-AMOUNT-CENTS.md, FEATURE-EXIT-CODES.md, DATABASE.md |

## Purpose

After a command's changes and before commit, sums each account's transaction amounts in integer
cents. Any account whose balance is below zero causes the command to roll back and exit 3. Balance
is the sum of transaction amounts; a balance of exactly zero is allowed.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC balance-overdraft-post-rejected ===
Intent: A post that would leave an account below zero exits 3 and stores nothing.

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
assert cli_runner("txn", "post", "CASH1", "SALES", "10.00", "2026-01-01")[0] == 0
before = cli_runner("count")[1]
assert cli_runner("txn", "post", "CASH1", "SALES", "-10.01", "2026-01-02")[0] == 3
assert cli_runner("txn", "get", "2")[0] == 4
assert cli_runner("count")[1] == before
=== END AC balance-overdraft-post-rejected ===

=== AC balance-overdraft-amend-rejected ===
Intent: An amend that would leave an account below zero exits 3 and leaves the stored amount unchanged.

import os
import tempfile
from cli.testing import cli_runner

work = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.path.join(work, "ledger.db")
categories = os.path.join(work, "categories.csv")
with open(categories, "w") as handle:
    handle.write("category,description\nSALES,Sales receipts\n")
amount_text = "10.00"

assert cli_runner("init")[0] == 0
assert cli_runner("account", "add", "CASH1", "Cash Box")[0] == 0
assert cli_runner("load", "categories", categories)[0] == 0
assert cli_runner("txn", "post", "CASH1", "SALES", amount_text, "2026-01-01")[0] == 0
assert cli_runner("txn", "amend", "1", "-1.00")[0] == 3
row = cli_runner("txn", "get", "1")[1].splitlines()[1]
assert row.split(",")[4] == amount_text
=== END AC balance-overdraft-amend-rejected ===

=== AC balance-overdraft-delete-rejected ===
Intent: A delete that would leave an account below zero exits 3 and keeps the row.

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
assert cli_runner("txn", "post", "CASH1", "SALES", "10.00", "2026-01-01")[0] == 0
assert cli_runner("txn", "post", "CASH1", "SALES", "-4.00", "2026-01-02")[0] == 0
assert cli_runner("txn", "delete", "1")[0] == 3
assert cli_runner("txn", "get", "1")[0] == 0
=== END AC balance-overdraft-delete-rejected ===

=== AC balance-overdraft-transfer-rejected ===
Intent: A transfer that would leave its from-account below zero exits 3 and stores neither row.

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
assert cli_runner("transfer", "CASH1", "CASH2", "1.00", "2026-01-02")[0] == 3
assert cli_runner("count")[1] == before
assert cli_runner("txn", "get", "1")[0] == 4
=== END AC balance-overdraft-transfer-rejected ===

=== AC balance-zero-accepted ===
Intent: A command that leaves an account balance of exactly zero succeeds.

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
assert cli_runner("txn", "post", "CASH1", "SALES", "10.00", "2026-01-01")[0] == 0
assert cli_runner("txn", "post", "CASH1", "SALES", "-10.00", "2026-01-02")[0] == 0
assert cli_runner("txn", "get", "2")[0] == 0
=== END AC balance-zero-accepted ===

## User Acceptance

- None.

## Guardrails

- Balances are computed in integer cents from stored rows, never from floating point.
- A rejected balance check always rolls back the whole command; no partial change persists.
