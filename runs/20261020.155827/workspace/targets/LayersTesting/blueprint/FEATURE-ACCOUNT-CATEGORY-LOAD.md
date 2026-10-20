# FEATURE: Account and Category Loading

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Loads validated account and category CSV files atomically through the ledger CLI. |
| Depends On  | FEATURE-SCHEMA-LIFECYCLE.md, DATABASE.md |
| Provides    | ledger load accounts, ledger load categories |
| Consumes    | ./ledger executable, ledger persistence operations |

## Inputs

Account files must have the header `account,name`. Category files must have the header `category,description`. Codes contain 1–12 uppercase letters or digits. Names and descriptions contain 1–40 characters and no commas or newlines.

Each load is one transaction. Duplicate keys, malformed headers, unreadable files, invalid fields, or constraint violations reject the entire batch with exit code 3 for rejected data or 1 for operational failure.

## Output

A successful load emits:

```text
table,loaded
<table>,<rows>
```

## Programmatic Acceptance

=== AC load-accounts-round-trip ===
Intent: A valid account CSV loads and becomes visible in the count and account interface.

import os
import subprocess
import tempfile
from pathlib import Path

accounts = "account,name\nA1,Main\nA2,Reserve\n"

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "ledger.db"
    csv_file = Path(directory) / "accounts.csv"
    csv_file.write_text(accounts)
    env = {**os.environ, "DATABASE_URL": str(database)}

    initialized = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(initialized.stdout)
    print(initialized.stderr)
    assert initialized.returncode == 0

    loaded = subprocess.run(["./ledger", "load", "accounts", str(csv_file)], capture_output=True, text=True, env=env)
    print(loaded.stdout)
    print(loaded.stderr)
    assert loaded.returncode == 0

    counted = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(counted.stdout)
    print(counted.stderr)
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1] == "accounts,2"
=== END AC load-accounts-round-trip ===

=== AC load-categories-round-trip ===
Intent: A valid category CSV loads and becomes visible in the count.

import os
import subprocess
import tempfile
from pathlib import Path

categories = "category,description\nSALES,Sales\nSUPPLY,Supplies\n"

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "ledger.db"
    csv_file = Path(directory) / "categories.csv"
    csv_file.write_text(categories)
    env = {**os.environ, "DATABASE_URL": str(database)}

    initialized = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(initialized.stdout)
    print(initialized.stderr)
    assert initialized.returncode == 0

    loaded = subprocess.run(["./ledger", "load", "categories", str(csv_file)], capture_output=True, text=True, env=env)
    print(loaded.stdout)
    print(loaded.stderr)
    assert loaded.returncode == 0

    counted = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(counted.stdout)
    print(counted.stderr)
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[2] == "categories,2"
=== END AC load-categories-round-trip ===

=== AC load-rollback-invalid ===
Intent: A rejected account batch leaves the target table unchanged.

import os
import subprocess
import tempfile
from pathlib import Path

accounts = "account,name\nA1,Main\nINVALID-CODE,Rejected\n"

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "ledger.db"
    csv_file = Path(directory) / "accounts.csv"
    csv_file.write_text(accounts)
    env = {**os.environ, "DATABASE_URL": str(database)}

    initialized = subprocess.run(["./ledger", "init"], capture_output=True, text=True, env=env)
    print(initialized.stdout)
    print(initialized.stderr)
    assert initialized.returncode == 0

    rejected = subprocess.run(["./ledger", "load", "accounts", str(csv_file)], capture_output=True, text=True, env=env)
    print(rejected.stdout)
    print(rejected.stderr)
    assert rejected.returncode == 3
    assert rejected.stdout == ""

    counted = subprocess.run(["./ledger", "count"], capture_output=True, text=True, env=env)
    print(counted.stdout)
    print(counted.stderr)
    assert counted.returncode == 0
    assert counted.stdout.splitlines()[1] == "accounts,0"
=== END AC load-rollback-invalid ===

## User Acceptance

- None.

## Guardrails

- Loads must validate the complete file before commit.
- A rejected batch must leave its target table unchanged.
- Application code must not read or modify the staged seed files except when the user supplies their path to `ledger load`.
- Loaded values must be persisted through the shipped persistence library.

## Database Interface

- `FEATURE-LEDGER-006` — read-write: categories.create - supplies: — - returns: —
