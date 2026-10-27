# FEATURE: Load Accounts

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implement `ledger load accounts <csv>` as an all-or-nothing bulk load. |
| Depends On | FEATURE-DatabaseSelection.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger load accounts |
| Consumes | ledgerlib.config, ledgerlib.validation, ledgerlib.csvout |

## Purpose

`cli/commands/load.py` owns `ledger load <table> <csv>` with a per-table handler registry; an unknown table is a usage error (exit 2). This story adds the `accounts` handler. The whole file is accepted or none of it is stored.

## Behavior

- The header must be exactly `account,name`; any other header is rejected with exit 3.
- Every data row must have the header's field count; each code and name is validated with `ledgerlib.validation`.
- A duplicate code within the file, or one already stored, is rejected with exit 3.
- Every check completes before the first write. Writes happen in one database transaction, so a rejected file stores nothing.
- A file that cannot be read exits 1 with nothing on standard output.
- A header-only file loads zero rows, prints `accounts,0`, and exits 0.
- Output is `table,loaded` followed by `accounts,<rows>`.
- Missing arguments or extra arguments are a usage error (exit 2).

## Database Interface

- `FEATURE-LEDGER-001` — write: create an account - supplies: `account`, `name` - returns: `account`, `name`
- `FEATURE-LEDGER-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-accounts-success ===
Intent: A valid accounts file stores every row, prints the loaded count, and the rows read back through the persistence interface.

import csv
import io
import os
import tempfile
from persistence.testing import db_session
from cli.testing import cli_runner

records = [("ZZLA1", "Load One"), ("ZZLA2", "Load Two"), ("ZZLA3", "Load Three")]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(records)
    with db_session() as db:
        code, out, err = cli_runner("load", "accounts", path)
        print(out)
        print(err)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        assert rows[0] == ["table", "loaded"]
        assert rows[1] == ["accounts", str(len(records))]
        assert len(rows) == 2
        for acct, name in records:
            got = db.accounts.get(account=acct)
            assert got is not None
            assert got.name == name
=== END AC load-accounts-success ===

=== AC load-accounts-header-only ===
Intent: A file with a valid header and no data rows loads zero rows, prints a zero count, and exits 0.

import csv
import io
import os
import tempfile
from persistence.testing import db_session
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "accounts.csv")
    with open(path, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow(["account", "name"])
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        print(out)
        print(err)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        assert rows == [["table", "loaded"], ["accounts", "0"]]
        assert len(db.accounts.list()) == before
=== END AC load-accounts-header-only ===

=== AC load-accounts-rejects-atomic ===
Intent: A file with a bad row, duplicate code, wrong header or short row exits 3 with empty standard output and stores none of its rows.

import csv
import os
import tempfile
from persistence.testing import db_session
from cli.testing import cli_runner

good = ("ZZLB1", "Atomic One")
cases = {
    "invalid-code": [["account", "name"], list(good), ["bad code", "Atomic Two"]],
    "duplicate-in-file": [["account", "name"], list(good), ["ZZLB1", "Atomic Dup"]],
    "wrong-header": [["code", "name"], list(good)],
    "short-row": [["account", "name"], list(good), ["ZZLB2"]],
    "empty-name": [["account", "name"], list(good), ["ZZLB3", ""]],
}
with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        before = len(db.accounts.list())
        for label, rows in cases.items():
            path = os.path.join(d, label + ".csv")
            with open(path, "w", newline="") as fh:
                csv.writer(fh, lineterminator="\n").writerows(rows)
            code, out, err = cli_runner("load", "accounts", path)
            print(label, code, err)
            assert code == 3
            assert out == ""
            assert err != ""
            assert db.accounts.get(account=good[0]) is None
            assert len(db.accounts.list()) == before
=== END AC load-accounts-rejects-atomic ===

=== AC load-accounts-duplicate-stored ===
Intent: A file naming an account that is already stored is rejected with exit 3 and its other rows are not stored.

import csv
import os
import tempfile
from persistence.testing import db_session
from cli.testing import cli_runner

stored = "ZZLC1"
fresh = "ZZLC2"
original = "Stored Name"
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow([fresh, "Fresh"])
        w.writerow([stored, "Replacement"])
    with db_session() as db:
        db.accounts.create(account=stored, name=original)
        code, out, err = cli_runner("load", "accounts", path)
        print(err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=fresh) is None
        kept = db.accounts.get(account=stored)
        assert kept is not None
        assert kept.name == original
=== END AC load-accounts-duplicate-stored ===

=== AC load-accounts-operational-and-usage ===
Intent: An unreadable file exits 1, an unknown table or a missing file argument exits 2, and each leaves standard output empty.

import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    missing = os.path.join(d, "no-such-file.csv")
    code, out, err = cli_runner("load", "accounts", missing)
    assert code == 1
    assert out == ""
    assert err != ""

    code, out, err = cli_runner("load", "nosuchtable", missing)
    assert code == 2
    assert out == ""

    code, out, err = cli_runner("load", "accounts")
    assert code == 2
    assert out == ""
=== END AC load-accounts-operational-and-usage ===

## User Acceptance

- None.

## Guardrails

- A rejected load changes nothing: all validation precedes the first write.
- Application code never reads `sources/run.sh` or any seed file; seed files reach the database only through `ledger load`.
- Loading uses the persistence library only; no database driver is opened here.
