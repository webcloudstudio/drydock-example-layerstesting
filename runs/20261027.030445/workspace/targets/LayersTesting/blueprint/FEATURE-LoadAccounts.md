# FEATURE: Load Accounts

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The shared `ledger load` command with its validators, and the accounts loader that stores a valid file in full or not at all. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-LedgerCli.md |
| Provides | ledger load, ledger load accounts |
| Consumes | ledger, accounts |

## Purpose

`ledger load <table> <csv>` loads `accounts`, `categories`, or `transactions` from a CSV file whose
header equals the table's columns in order. This story creates the shared `load` command (argument
checks, table dispatch, file reading, header check, the registry that later table loaders join) and
the shared code and name validators, and registers the `accounts` loader.

## Behavior

- Exactly two arguments (table, csv path) are required; any other count is a usage error, exit 2.
- An unknown table is a usage error, exit 2.
- A file that cannot be read is an operational failure, exit 1.
- The first line must equal the table's columns in order (`account,name` for accounts). A mismatch is
  rejected, exit 3 (Plan decision Q-003).
- Codes are 1 to 12 characters from `A-Z` and `0-9`. Names are 1 to 40 characters and contain no comma
  or newline.
- Every row is validated, and duplicate keys are detected both within the file and against stored
  accounts, before the first write. Any failure exits 3, writes nothing to standard output, writes one
  diagnostic line to standard error, and stores none of the rows.
- On success all rows are stored in one persistence-library transaction. Standard output is
  `table,loaded` followed by `accounts,<rows>`. A file with a valid header and no data rows stores
  nothing, writes `accounts,0`, and exits 0.
- The shared validators (`validate_code`, `validate_text`) are importable by later stories.

## Database Interface

- `FEATURE-ACCOUNT-001` — write: store an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-ACCOUNT-002` — read: detect an existing account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-success ===
Intent: A valid accounts file exits 0, reports the loaded count in the specified two-row CSV, and every row is readable afterward.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZQL01", "Load One"], ["ZQL02", "Load Two"], ["ZQL03", "Load Three"]]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["accounts", str(len(rows))]]
        assert len(db.accounts.list()) == before + len(rows)
        for acct, name in rows:
            stored = db.accounts.get(account=acct)
            assert stored is not None
            assert stored.name == name
=== END AC load-accounts-success ===

=== AC load-accounts-header-only ===
Intent: A file holding only a valid header loads zero rows, reports zero, exits 0, and changes nothing.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow(["account", "name"])
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["accounts", "0"]]
        assert len(db.accounts.list()) == before
=== END AC load-accounts-header-only ===

=== AC load-accounts-duplicate-in-file ===
Intent: A repeated code inside one file is rejected with exit 3, empty stdout, and none of the file's rows stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

rows = [["ZQL11", "First"], ["ZQL12", "Second"], ["ZQL11", "Again"]]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.accounts.list()) == before
        assert db.accounts.get(account="ZQL11") is None
        assert db.accounts.get(account="ZQL12") is None
=== END AC load-accounts-duplicate-in-file ===

=== AC load-accounts-duplicate-stored ===
Intent: A code that already exists in the store rejects the whole file with exit 3 and leaves the stored row and the file's other rows untouched.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

existing = "ZQL21"
kept_name = "Original"
fresh = "ZQL22"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow([fresh, "Fresh"])
        w.writerow([existing, "Replacement"])
    with db_session() as db:
        db.accounts.create(account=existing, name=kept_name)
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.accounts.list()) == before
        assert db.accounts.get(account=existing).name == kept_name
        assert db.accounts.get(account=fresh) is None
=== END AC load-accounts-duplicate-stored ===

=== AC load-accounts-invalid-rows ===
Intent: Each rule violation (lowercase code, over-long code, empty name, over-long name, comma in name) after a valid first row exits 3 and stores neither row.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = ["ZQL31", "Good Row"]
bad_rows = [
    ["zql32", "Lowercase code"],
    ["A" * 13, "Long code"],
    ["ZQL33", ""],
    ["ZQL34", "N" * 41],
    ["ZQL35", "has,comma"],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        before = len(db.accounts.list())
        for i, bad in enumerate(bad_rows):
            path = os.path.join(tmp, "accounts%d.csv" % i)
            with open(path, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["account", "name"])
                w.writerow(good)
                w.writerow(bad)
            code, out, err = cli_runner("load", "accounts", path)
            print(i, code, out, err)
            assert code == 3
            assert out == ""
            assert db.accounts.get(account=good[0]) is None
            assert len(db.accounts.list()) == before
=== END AC load-accounts-invalid-rows ===

=== AC load-accounts-header-mismatch ===
Intent: A header that does not equal the table columns in order is rejected with exit 3 and nothing stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["name", "account"])
        w.writerow(["Swapped", "ZQL41"])
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.accounts.list()) == before
=== END AC load-accounts-header-mismatch ===

=== AC load-accounts-usage-and-unreadable ===
Intent: An unknown table or wrong argument count exits 2, and an unreadable file exits 1, each with empty stdout.

import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.csv")
    code, out, err = cli_runner("load", "accounts", missing)
    print(out, err)
    assert code == 1
    assert out == ""
    code, out, err = cli_runner("load", "nosuchtable", missing)
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("load", "accounts")
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("load", "accounts", missing, "extra")
    assert code == 2
    assert out == ""
=== END AC load-accounts-usage-and-unreadable ===

## User Acceptance

- None.

## Guardrails

- No row is stored when any row, header, or key check fails.
- Application code never reads `sources/run.sh` or a seed file; files reach the database only through this command.
- Diagnostics go to standard error only.
- Persistence is reached only through the `persistence` package.
