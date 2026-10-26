# FEATURE: Load Accounts

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implement `ledger load accounts <csv>` as an all-or-nothing bulk load. |
| Depends On | FEATURE-LedgerInit.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger load accounts |
| Consumes | ledger.register_command, persistence.open_database, validation.check_code, validation.check_text, csv_output.write_rows, ledger_errors.Rejected, ledger_errors.OperationalFailure |

## Purpose

Load account records from a CSV file. The whole file is checked before the first write, so a
rejected file stores nothing.

## Rules

- Register the `accounts` table under `load`; the command takes the table name and one file path.
- An unreadable file raises `OperationalFailure` (exit 1).
- Parse the whole file with the standard `csv` module. The header must equal `account,name` exactly, in names and order; any other header raises `Rejected` (exit 3) before any row is stored. An empty file counts as a wrong header.
- Every data row must have exactly two fields. Validate `account` with `validation.check_code` and `name` with `validation.check_text` (1 to 40 characters, no comma or newline). Any bad row rejects the file.
- A code that repeats within the file, or that already exists in the store (`db.accounts.get`), rejects the whole file. Account names may repeat across accounts.
- Only after every check passes, insert all rows with `db.accounts.create` in one database transaction. If an insert fails the transaction rolls back and nothing is stored.
- A header-only file loads zero rows.
- On success write `table,loaded` and `accounts,<rows>` through `csv_output.write_rows` and exit 0. A failure writes nothing to standard output.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: check whether an account code already exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-ACCOUNT-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-success ===
Intent: A valid file stores every row and reports the loaded count.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

header = ["account", "name"]
rows = [["ZQLA1", "Load One"], ["ZQLA2", "Load Two"], ["ZQLA3", "Load Two"]]
with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "accounts.csv")
        with open(path, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows([header] + rows)
        code, out, err = cli_runner("load", "accounts", path)
    print(err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["table", "loaded"], ["accounts", str(len(rows))]]
    stored = [[r.account, r.name] for r in db.accounts.list()]
    assert stored == sorted(rows)
=== END AC load-accounts-success ===

=== AC load-accounts-header-only ===
Intent: A header-only file loads zero rows and reports zero.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

header = ["account", "name"]
with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "accounts.csv")
        with open(path, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows([header])
        code, out, err = cli_runner("load", "accounts", path)
    print(err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["table", "loaded"], ["accounts", "0"]]
    assert db.accounts.list() == []
=== END AC load-accounts-header-only ===

=== AC load-accounts-bad-header ===
Intent: A header differing in name or order is rejected with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    for header in (["name", "account"], ["account", "title"], ["account"]):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "accounts.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(header)
                w.writerow(["ZQLB1", "Bad Header"][: len(header)])
            code, out, err = cli_runner("load", "accounts", path)
        print(header, code, err)
        assert code == 3
        assert out == ""
        assert db.accounts.list() == []
=== END AC load-accounts-bad-header ===

=== AC load-accounts-bad-row-stores-nothing ===
Intent: One invalid row rejects the whole file; earlier valid rows are not stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

header = ["account", "name"]
long_name = "N" * 41
cases = {
    "lowercase code": [["ZQLC1", "Fine One"], ["zqlc2", "Fine Two"]],
    "long name": [["ZQLC3", "Fine One"], ["ZQLC4", long_name]],
    "extra field": [["ZQLC5", "Fine One"], ["ZQLC6", "Fine Two", "surplus"]],
    "empty name": [["ZQLC7", "Fine One"], ["ZQLC8", ""]],
    "repeated code": [["ZQLC9", "Fine One"], ["ZQLC9", "Fine Two"]],
}
with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    for label, rows in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "accounts.csv")
            with open(path, "w", newline="") as fh:
                csv.writer(fh, lineterminator="\n").writerows([header] + rows)
            code, out, err = cli_runner("load", "accounts", path)
        print(label, code, err)
        assert code == 3, label
        assert out == "", label
        assert db.accounts.list() == [], label
=== END AC load-accounts-bad-row-stores-nothing ===

=== AC load-accounts-duplicate-of-stored ===
Intent: A file repeating a stored code is rejected and its new rows are not stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

header = ["account", "name"]
existing = "ZQLD1"
fresh = "ZQLD2"
with db_session() as db:
    code, out, err = cli_runner("init")
    assert code == 0
    db.accounts.create(account=existing, name="Already Here")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "accounts.csv")
        with open(path, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows(
                [header, [fresh, "New One"], [existing, "Replacement"]]
            )
        code, out, err = cli_runner("load", "accounts", path)
    print(err)
    assert code == 3
    assert out == ""
    assert db.accounts.get(account=fresh) is None
    assert db.accounts.get(account=existing).name == "Already Here"
=== END AC load-accounts-duplicate-of-stored ===

=== AC load-accounts-unreadable-file ===
Intent: A missing file exits 1 and changes nothing.

import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.accounts.create(account="ZQLE1", name="Untouched")
    before = [r.account for r in db.accounts.list()]
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "missing.csv")
        code, out, err = cli_runner("load", "accounts", path)
    print(err)
    assert code == 1
    assert out == ""
    assert [r.account for r in db.accounts.list()] == before
=== END AC load-accounts-unreadable-file ===

=== AC load-accounts-usage ===
Intent: A missing path or an unknown table is a usage error.

from cli.testing import cli_runner

code, out, err = cli_runner("load", "accounts")
assert code == 2 and out == ""
code, out, err = cli_runner("load", "nosuch", "ignored.csv")
assert code == 2 and out == ""
=== END AC load-accounts-usage ===

## User Acceptance

- None.

## Guardrails

- The whole file is validated before the first write; a rejected file stores no row.
- Seed files reach the database only through this command; application code never reads them directly.
- A failing command writes nothing to standard output and one diagnostic line to standard error that never contains a DSN or credential.
