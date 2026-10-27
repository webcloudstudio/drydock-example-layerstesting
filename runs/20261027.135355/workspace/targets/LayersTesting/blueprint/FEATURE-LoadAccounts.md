# FEATURE: Load Accounts

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger load accounts <csv>` as an all-or-nothing bulk load. |
| Depends On | FEATURE-LoadCsvReader.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger load accounts |
| Consumes | ledger_core.csvio, ledger_core.validation, cli.registry |

## Purpose

Load accounts from a CSV file whose header is `account,name`. Every row is validated before the
first write; the rows are then written together or not at all.

## Behavior

1. `ledger load accounts <csv>` takes exactly one file argument; other counts exit 2.
2. Read the file with `ledger_core.csvio.read_rows(path, ("account", "name"))`. An unreadable file
   exits 1; a wrong header or wrong field count exits 3.
3. Validate every row before any write: the code is 1 to 12 characters of `A-Z0-9`, the name is 1
   to 40 characters with no comma or newline, the code does not repeat within the file, and the code
   is not already stored.
4. Insert every row in one atomic unit. A failure at any row leaves every earlier row unstored.
5. Print `table,loaded` then `accounts,<rows>`, where `<rows>` is the number of rows inserted.
6. Any rejection exits 3 with nothing on standard output and one diagnostic line on standard error.
   A header-only file loads zero rows and prints `accounts,0`.

## Database Interface

- `FEATURE-ACCOUNT-005` — read: list stored accounts to detect duplicate keys - supplies: — - returns: `account`, `name`
- `FEATURE-ACCOUNT-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-success ===
Intent: a valid accounts file loads every row, prints the declared two CSV rows with the loaded count, and the rows are readable afterward.
Requires: executable=python3; scope=test

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZZLAA1", "Load One"], ["ZZLAA2", "Load Two"], ["ZZLAA3", "Load Three"]]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["accounts", str(len(rows))]]
        for acct, name in rows:
            row = db.accounts.get(account=acct)
            assert row is not None
            got = row["name"] if isinstance(row, dict) else row.name
            assert got == name
=== END AC load-accounts-success ===

=== AC load-accounts-rejected-row-stores-nothing ===
Intent: when the last row is invalid, exit 3 is returned, stdout is empty, and none of the earlier valid rows is stored.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["ZZLB%d" % i, "Good %d" % i] for i in range(1, 11)]
bad = ["zzlbbad", "Lowercase Code"]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(good)
        w.writerow(bad)
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        assert code == 3
        assert out == ""
        assert len(db.accounts.list()) == before
        for acct, _ in good:
            assert db.accounts.get(account=acct) is None
=== END AC load-accounts-rejected-row-stores-nothing ===

=== AC load-accounts-invalid-fields ===
Intent: each invalid code or name (too long, empty, bad characters, comma in name) rejects the whole file with exit 3 and stores neither it nor the valid row before it.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

first = ["ZZLCOK", "Valid First"]
bad_rows = [
    ["ABCDEFGHIJKLM", "Code Too Long"],
    ["ZZLC-1", "Bad Char Code"],
    ["", "Empty Code"],
    ["ZZLC2", ""],
    ["ZZLC3", "x" * 41],
    ["ZZLC4", "has,comma"],
]
with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        for i, bad in enumerate(bad_rows):
            path = os.path.join(d, "a%d.csv" % i)
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["account", "name"])
                w.writerow(first)
                w.writerow(bad)
            code, out, err = cli_runner("load", "accounts", path)
            assert code == 3, bad
            assert out == ""
            assert db.accounts.get(account=first[0]) is None
=== END AC load-accounts-invalid-fields ===

=== AC load-accounts-duplicates-rejected ===
Intent: a code repeated inside the file, and a code already stored, each reject the whole file with exit 3 and leave the other rows unstored.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)

with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        p1 = os.path.join(d, "dup_in_file.csv")
        write(p1, [["ZZLD1", "One"], ["ZZLD2", "Two"], ["ZZLD1", "One Again"]])
        code, out, err = cli_runner("load", "accounts", p1)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account="ZZLD1") is None
        assert db.accounts.get(account="ZZLD2") is None

        stored = "ZZLD3"
        stored_name = "Already Stored"
        db.accounts.create(account=stored, name=stored_name)
        p2 = os.path.join(d, "dup_stored.csv")
        write(p2, [["ZZLD4", "Fresh"], [stored, "Replacement"]])
        code, out, err = cli_runner("load", "accounts", p2)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account="ZZLD4") is None
        row = db.accounts.get(account=stored)
        got = row["name"] if isinstance(row, dict) else row.name
        assert got == stored_name
=== END AC load-accounts-duplicates-rejected ===

=== AC load-accounts-header-and-usage ===
Intent: a wrong header exits 3 with nothing stored, and a missing file argument is a usage error with exit 2.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "wrong_header.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["code", "name"])
        w.writerow(["ZZLE1", "Wrong Header"])
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", path)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account="ZZLE1") is None
        code, out, err = cli_runner("load", "accounts")
        assert code == 2
        assert out == ""
=== END AC load-accounts-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- No row is written until every row in the file has been validated.
- Seed files are never read by application code; the file path comes only from the command line.
- A failing command writes nothing to standard output.
