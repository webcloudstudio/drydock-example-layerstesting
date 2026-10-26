# FEATURE: Load Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Implements `ledger load accounts <csv>` with all-or-nothing validation of the whole file. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md |
| Provides    | ledger load accounts |
| Consumes    | accounts.create, accounts.get |

## Purpose

Bulk-load accounts from a CSV file whose header is exactly `account,name`. The command checks
every row and every rule before its first write, so a file with one invalid row stores nothing.

## Trigger

`./ledger load accounts <csv>`

## Sequence

1. Reject a wrong argument count or an unknown table with exit 2.
2. Read the file. An unreadable file exits 1.
3. Require the header `account,name`; any other header exits 3.
4. Validate every data row: the code is 1 to 12 characters from `A-Z` and `0-9`; the name is 1 to
   40 characters with no comma or newline; a row with the wrong number of fields is invalid.
5. Reject (exit 3) a code that repeats within the file or already exists in `accounts`.
6. Only after every row passed, write all rows through `accounts.create`.
7. Print `table,loaded` and `accounts,<rows>` as CSV with `\n` endings.

A failing command writes nothing to standard output and one diagnostic line to standard error.

## Reads

- `accounts.get` for each code in the file, to detect duplicates with stored rows.

## Writes

- `accounts.create` once per validated row, after all validation has passed.

## Database Interface

- `FEATURE-ACCOUNTS-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNTS-002` — read: find a stored account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-valid ===
Intent: A valid accounts file loads, reports the loaded count, and every row reads back from the store.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["UTLA1", "Load One"], ["UTLA2", "Load Two"], ["UTLA3", "Load Three"]]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", path)
        print(out)
        print(err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["accounts", str(len(rows))]]
        for account, name in rows:
            stored = db.accounts.get(account=account)
            assert stored is not None
            assert stored.name == name
=== END AC load-accounts-valid ===

=== AC load-accounts-atomic-invalid-row ===
Intent: A file with an invalid last row exits 3, prints nothing to stdout, and stores none of the preceding valid rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["UTLB1", "Good One"], ["UTLB2", "Good Two"]]
bad = ["utlb3", "Lowercase Code"]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(good)
        w.writerow(bad)
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", path)
        print(err)
        assert code == 3
        assert out == ""
        for account, _ in good:
            assert db.accounts.get(account=account) is None
        assert db.accounts.get(account=bad[0]) is None
=== END AC load-accounts-atomic-invalid-row ===

=== AC load-accounts-field-rules ===
Intent: Over-long codes, empty names, and over-long names each reject the whole file with exit 3 and store nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

anchor = ["UTLC0", "Anchor"]
variants = [
    ["A" * 13, "Long Code"],
    ["UTLC1", ""],
    ["UTLC2", "N" * 41],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        for index, variant in enumerate(variants):
            path = os.path.join(tmp, f"accounts{index}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["account", "name"])
                w.writerow(anchor)
                w.writerow(variant)
            code, out, err = cli_runner("load", "accounts", path)
            print(err)
            assert code == 3
            assert out == ""
            assert db.accounts.get(account=anchor[0]) is None
=== END AC load-accounts-field-rules ===

=== AC load-accounts-duplicates ===
Intent: A code repeated inside the file, or already stored, rejects the whole file with exit 3 and stores nothing new.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

stored_code = "UTLD1"
fresh = "UTLD2"
repeated = "UTLD3"
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.accounts.create(account=stored_code, name="Already Here")

        against_store = os.path.join(tmp, "store.csv")
        with open(against_store, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["account", "name"])
            w.writerow([fresh, "Fresh"])
            w.writerow([stored_code, "Clash"])
        code, out, err = cli_runner("load", "accounts", against_store)
        print(err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=fresh) is None
        assert db.accounts.get(account=stored_code).name == "Already Here"

        within = os.path.join(tmp, "within.csv")
        with open(within, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["account", "name"])
            w.writerow([repeated, "First"])
            w.writerow([repeated, "Second"])
        code, out, err = cli_runner("load", "accounts", within)
        print(err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=repeated) is None
=== END AC load-accounts-duplicates ===

=== AC load-accounts-header-and-usage ===
Intent: A mismatched header exits 3, a missing file exits 1, and a wrong argument count or unknown table exits 2.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    wrong = os.path.join(tmp, "wrong.csv")
    with open(wrong, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["name", "account"])
        w.writerow(["Swapped", "UTLE1"])
    missing = os.path.join(tmp, "absent.csv")
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", wrong)
        assert code == 3 and out == ""
        assert db.accounts.get(account="UTLE1") is None
        code, out, err = cli_runner("load", "accounts", missing)
        assert code == 1 and out == ""
        code, out, err = cli_runner("load", "accounts")
        assert code == 2 and out == ""
        code, out, err = cli_runner("load", "accounts", wrong, wrong)
        assert code == 2 and out == ""
        code, out, err = cli_runner("load", "nosuchtable", wrong)
        assert code == 2 and out == ""
=== END AC load-accounts-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- Validate every row and rule before the first write; a rejected load changes nothing.
- Do not read `sources/` seed files from application code; they reach the database only through this command.
- Open no database driver outside the shipped persistence library.
- Diagnostics go to standard error only and are never compared.
