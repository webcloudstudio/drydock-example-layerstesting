# FEATURE: Schema Lifecycle

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Implements ledger initialization and ordered row counting. |
| Depends On  | FEATURE-CLI-FOUNDATION.md, DATABASE.md |
| Provides    | ledger init, ledger count |
| Consumes    | ./ledger executable, ledger persistence operations |

## Behavior

`ledger init` drops and recreates the accounts, categories, and transactions tables, leaving all three empty and producing no output.

`ledger count` reports rows in the fixed order accounts, categories, transactions using:

```text
table,rows
```

## Programmatic Acceptance

=== AC schema-init-empty ===
Intent: Initialization creates an empty ledger schema and emits no output.

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "DATABASE_URL": os.path.join(directory, "ledger.db")}
    result = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
    assert result.stdout == ""

    counted = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(counted.stdout)
    print(counted.stderr)
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[0] == "table,rows"
    assert counted.stdout.splitlines()[1:] == ["accounts,0", "categories,0", "transactions,0"]
=== END AC schema-init-empty ===

=== AC schema-count-order ===
Intent: Count reports all declared tables in the required order.

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "DATABASE_URL": os.path.join(directory, "ledger.db")}
    initialized = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(initialized.stdout)
    print(initialized.stderr)
    assert initialized.returncode == 0

    result = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
    rows = result.stdout.splitlines()
    assert rows[0] == "table,rows"
    assert [row.split(",")[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
=== END AC schema-count-order ===

=== AC schema-reinitializes ===
Intent: A later initialization removes previously stored rows.

import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    env = {**os.environ, "DATABASE_URL": os.path.join(directory, "ledger.db")}
    first = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(first.stdout)
    print(first.stderr)
    assert first.returncode == 0

    added = subprocess.run(["./ledger", "account", "add", "TEMP", "Temporary"], capture_output=True, text=True, env=env)
    print(added.stdout)
    print(added.stderr)
    assert added.returncode == 0

    reset = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(reset.stdout)
    print(reset.stderr)
    assert reset.returncode == 0

    counted = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(counted.stdout)
    print(counted.stderr)
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1:] == ["accounts,0", "categories,0", "transactions,0"]
=== END AC schema-reinitializes ===

## User Acceptance

- None.

## Guardrails

- `init` must emit no standard output.
- `count` must use database state and never hardcode row counts.
- Initialization must affect all three tables atomically.

## Database Interface

- `FEATURE-LEDGER-001` — write: accounts.delete - supplies: — - returns: —
- `FEATURE-LEDGER-002` — read: accounts.list - supplies: — - returns: —
- `FEATURE-LEDGER-014` — write: categories.delete - supplies: — - returns: —
- `FEATURE-LEDGER-015` — write: transactions.delete - supplies: — - returns: —
- `FEATURE-LEDGER-016` — read: categories.list - supplies: — - returns: —
- `FEATURE-LEDGER-017` — read: transactions.list - supplies: — - returns: —
