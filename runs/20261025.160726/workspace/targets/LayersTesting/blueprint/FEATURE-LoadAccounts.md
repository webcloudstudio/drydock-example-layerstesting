# FEATURE: Load Accounts

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger load accounts <csv>`, which loads accounts from a CSV file all-or-nothing. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, FEATURE-Init.md, FEATURE-Count.md |
| Provides | ledger load accounts |
| Consumes | cli.main, parse_amount, validate_code, validate_text |

## Purpose

Bulk-load account rows from a CSV file so the shop's drawers, safe, and petty cash exist before
transactions are loaded. The command either stores every row or stores nothing.

## Command Contract

`ledger load accounts <csv>` registers under the `load` command in the cli command table.

| Condition | Result |
|---|---|
| File readable, header equals `account,name`, every row valid | Exit 0. Stdout is `table,loaded` then `accounts,<rows>`. |
| Missing `<csv>` argument or extra arguments | Exit 2, nothing on stdout. |
| File missing or unreadable | Exit 1, nothing on stdout. |
| Header differs from the table columns in name or order | Exit 3, nothing stored. |
| A row has an invalid code or name (see Rules 3 and 4) | Exit 3, nothing stored. |
| A code repeats within the file | Exit 3, nothing stored. |
| A code already exists in the `accounts` table | Exit 3, nothing stored. |

## Behavior

1. Read the whole file and parse it with the standard `csv` module.
2. Check the header, then check every row with the `ledger-core` validators, the duplicate-in-file
   rule, and the duplicate-in-table rule. All checks complete before the first write.
3. Write every row in one transaction through the persistence library, then print the result.
4. A failing command writes one diagnostic line to standard error and nothing to standard output.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: detect codes already stored - supplies: `account` - returns: `account`, `name`

Rows are written through `db.accounts.create`, the operation declared for the account feature in
`DATABASE.md`; this feature reuses it and declares no operation of its own.

## Programmatic Acceptance

=== AC load-accounts-valid ===
Intent: A valid accounts file loads, reports the loaded count, and every row reads back.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

codes = ["LDACC1", "LDACC2", "LDACC3"]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows([[c, "Name " + c] for c in codes])
    before = counts()
    rc, out, err = cli_runner("load", "accounts", path)
print(out)
print(err)
assert rc == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["table", "loaded"], ["accounts", str(len(codes))]]
assert counts()["accounts"] == before["accounts"] + len(codes)
with db_session() as db:
    for c in codes:
        got = db.accounts.get(account=c)
        assert got is not None
        assert got.name == "Name " + c
=== END AC load-accounts-valid ===

=== AC load-accounts-header ===
Intent: A file whose header does not match the table columns is rejected with exit 3 and stores nothing.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

code = "LDHDR1"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["code", "label"])
        w.writerow([code, "Wrong Header"])
    rc, out, err = cli_runner("load", "accounts", path)
print(out)
print(err)
assert rc == 3
assert out == ""
with db_session() as db:
    assert db.accounts.get(account=code) is None
=== END AC load-accounts-header ===

=== AC load-accounts-atomic ===
Intent: An invalid row rejects the whole file so no earlier row is stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = "LDATM1"
bad = "bad code"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "accounts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow([good, "Good Row"])
        w.writerow([bad, "Bad Row"])
    rc, out, err = cli_runner("load", "accounts", path)
print(out)
print(err)
assert rc == 3
assert out == ""
with db_session() as db:
    assert db.accounts.get(account=good) is None
=== END AC load-accounts-atomic ===

=== AC load-accounts-duplicates ===
Intent: A code repeated inside the file, or already stored, is rejected with exit 3 and nothing is added.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerows(rows)

with tempfile.TemporaryDirectory() as tmp:
    dup_file = os.path.join(tmp, "dup.csv")
    write(dup_file, [["LDDUP1", "One"], ["LDDUP1", "Two"]])
    before = counts()
    rc, out, err = cli_runner("load", "accounts", dup_file)
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == before

    once = os.path.join(tmp, "once.csv")
    write(once, [["LDDUP2", "Only"]])
    rc, out, err = cli_runner("load", "accounts", once)
    assert rc == 0
    after_first = counts()
    rc, out, err = cli_runner("load", "accounts", once)
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == after_first
=== END AC load-accounts-duplicates ===

=== AC load-accounts-usage-and-io ===
Intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).

import os
import tempfile
from cli.testing import cli_runner

rc, out, err = cli_runner("load", "accounts")
print(out, err)
assert rc == 2
assert out == ""

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.csv")
    rc, out, err = cli_runner("load", "accounts", missing)
print(out, err)
assert rc == 1
assert out == ""
=== END AC load-accounts-usage-and-io ===

## User Acceptance

- None.

## Guardrails

- No account is stored unless every row of the file is valid.
- Application code never reads `sources/` seed files; the file path comes only from the command line.
- All database access goes through the shipped persistence library.
