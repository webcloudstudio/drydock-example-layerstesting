# FEATURE: Load Header Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | A load whose header does not match the table's columns in order exits 3; an unreadable file exits 1. |
| Depends On  | FEATURE-LOAD-TRANSACTIONS.md, FEATURE-ACCOUNT-001.md, DATABASE.md |
| Provides    | header validation for ledger load <table> <csv> |
| Consumes    | ledger load <table> <csv>, accounts.create, transactions.list |

## Purpose

Before any row is read, the loader compares the file's header with the table's declared columns.
The comparison is exact and ordered. A mismatch is a rejected file and exits 3. A file that cannot
be opened or read is an operational failure and exits 1.

## Behavior

- Column names must match the table's columns in the order given in `sources/INSTRUCTIONS.md`.
- A reordered, renamed, missing, or extra column is a mismatch.
- A mismatch stores no rows and changes no table.
- An unreadable or nonexistent file exits 1 and changes no table.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC load-header-mismatch ===
# Intent: A transaction load whose header columns are reordered exits 3 and stores no rows.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

reordered_header = "account,txn_id,date,category,amount,memo\n"
reordered_row = "DRAWER1,1,2026-04-01,SALES,10.00,reordered\n"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

mismatch_file = Path(tempfile.mkdtemp()) / "mismatch.csv"
mismatch_file.write_text(reordered_header + reordered_row)

exit_code, out, err = cli_runner("load", "transactions", str(mismatch_file))
print(out)
print(err, file=sys.stderr)
assert exit_code == 3

with db_session(dsn) as db:
    assert len(db.transactions.list()) == 0
=== END AC load-header-mismatch ===

=== AC load-header-unreadable ===
# Intent: A load of a file that does not exist exits 1 and changes no table.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

missing_file = Path(tempfile.mkdtemp()) / "does-not-exist.csv"
assert not missing_file.exists()

exit_code, out, err = cli_runner("init")
assert exit_code == 0

exit_code, out, err = cli_runner("load", "accounts", str(missing_file))
print(out)
print(err, file=sys.stderr)
assert exit_code == 1

with db_session(dsn) as db:
    assert len(db.accounts.list()) == 0
=== END AC load-header-unreadable ===

=== AC load-header-accounts-mismatch ===
# Intent: An accounts load whose header is missing a column exits 3 and stores no account rows.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = str(Path(tempfile.mkdtemp()) / "ledger.db")
os.environ["DATABASE_URL"] = dsn

short_header = "account\n"
short_row = "DRAWER1\n"

exit_code, out, err = cli_runner("init")
assert exit_code == 0

short_file = Path(tempfile.mkdtemp()) / "short.csv"
short_file.write_text(short_header + short_row)

exit_code, out, err = cli_runner("load", "accounts", str(short_file))
print(out)
print(err, file=sys.stderr)
assert exit_code == 3

with db_session(dsn) as db:
    assert len(db.accounts.list()) == 0
=== END AC load-header-accounts-mismatch ===

## User Acceptance

- None.

## Guardrails

- A header check runs before any row is stored. No partial load is ever committed.
