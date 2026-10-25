# FEATURE: Load Rejection

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Guarantees that a rejected `ledger load` exits 3 and leaves every table exactly as it was. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LoadTransactions.md, FEATURE-Count.md |
| Provides | atomic load rejection |
| Consumes | ledger load accounts, ledger load categories, ledger load transactions, ledger count |

## Purpose

Prove and enforce the all-or-nothing rule for loads: a file with one invalid row stores none of
its rows. A file of ten valid rows followed by an eleventh naming an unknown account stores none
of the eleven.

## Behavior

| Scenario | Result |
|---|---|
| Transactions file whose last row names an unknown account | Exit 3, nothing on stdout, no table changes. |
| Transactions file with an invalid amount, date, or duplicate id on a late row | Exit 3, no table changes. |
| Accounts file reloaded after it was loaded | Exit 3, no table changes. |
| Categories file reloaded after it was loaded | Exit 3, no table changes. |

Row counts of all three tables read through `ledger count` are identical before and after every
rejected command.

## Database Interface

- `FEATURE-TXN-002` — read: verify no transaction row was stored - supplies: `account` - returns: `txn_id`, `account`, `amount`
- `FEATURE-ACCOUNT-002` — read: verify no account row was stored - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC load-rejection-eleventh-row ===
Intent: Ten valid rows followed by an unknown-account row are rejected with exit 3 and none of the eleven is stored.

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

def load(table, header, rows, tmp, name=None):
    path = os.path.join(tmp, (name or table) + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

header = ["txn_id", "date", "account", "category", "amount", "memo"]
acct, cat = "LDRJA1", "LDRJC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
rows = [[base + i, "2026-05-01", acct, cat, "10.00", "batch %d" % i] for i in range(1, 11)]
rows.append([base + 11, "2026-05-01", "LDRJNONE", cat, "10.00", "unknown account"])
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Reject Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Reject Category"]], tmp)[0] == 0
    before = counts()
    rc, out, err = load("transactions", header, rows, tmp, "eleven")
print(out, err)
assert rc == 3
assert out == ""
assert counts() == before
with db_session() as db:
    for i in range(1, 12):
        assert db.transactions.get(txn_id=base + i) is None
=== END AC load-rejection-eleventh-row ===

=== AC load-rejection-staged-bad-file ===
Intent: The supplied bad transactions file is rejected with exit 3 and no table row count changes.

import csv
import io
from pathlib import Path
from cli.testing import cli_runner

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

bad = Path("sources") / "seed_transactions_bad.csv"
assert bad.is_file()
before = counts()
rc, out, err = cli_runner("load", "transactions", str(bad))
print(out, err)
assert rc == 3
assert out == ""
assert counts() == before
=== END AC load-rejection-staged-bad-file ===

=== AC load-rejection-late-invalid-fields ===
Intent: An invalid amount, invalid date, or duplicate id on a late row stores none of the earlier valid rows.

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

def load(table, header, rows, tmp, name=None):
    path = os.path.join(tmp, (name or table) + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

header = ["txn_id", "date", "account", "category", "amount", "memo"]
acct, cat = "LDRLA1", "LDRLC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
good = [
    [base + 1, "2026-05-01", acct, cat, "40.00", "first"],
    [base + 2, "2026-05-02", acct, cat, "40.00", "second"],
]
late = [
    [base + 3, "2026-05-03", acct, cat, "1.234", "bad amount"],
    [base + 4, "2026-02-30", acct, cat, "5.00", "bad date"],
    [base + 1, "2026-05-03", acct, cat, "5.00", "duplicate id"],
]
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Late Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Late Category"]], tmp)[0] == 0
    before = counts()
    for n, bad_row in enumerate(late, start=1):
        rc, out, err = load("transactions", header, good + [bad_row], tmp, "late%d" % n)
        print(n, out, err)
        assert rc == 3
        assert out == ""
        assert counts() == before
with db_session() as db:
    assert db.transactions.get(txn_id=base + 1) is None
    assert db.transactions.get(txn_id=base + 2) is None
=== END AC load-rejection-late-invalid-fields ===

=== AC load-rejection-reload-existing ===
Intent: Reloading accounts or categories that already exist is rejected with exit 3 and changes no table.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner

def counts():
    rc, out, err = cli_runner("count")
    assert rc == 0
    return {r[0]: int(r[1]) for r in list(csv.reader(io.StringIO(out)))[1:]}

def write(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)

with tempfile.TemporaryDirectory() as tmp:
    accounts = os.path.join(tmp, "accounts.csv")
    categories = os.path.join(tmp, "categories.csv")
    write(accounts, ["account", "name"], [["LDRRA1", "Reload A"], ["LDRRA2", "Reload B"]])
    write(categories, ["category", "description"], [["LDRRC1", "Reload C"]])
    assert cli_runner("load", "accounts", accounts)[0] == 0
    assert cli_runner("load", "categories", categories)[0] == 0
    before = counts()
    for table, path in (("accounts", accounts), ("categories", categories)):
        rc, out, err = cli_runner("load", table, path)
        print(table, out, err)
        assert rc == 3
        assert out == ""
        assert counts() == before
=== END AC load-rejection-reload-existing ===

## User Acceptance

- None.

## Guardrails

- A rejected load never leaves partial rows in any table.
- Rejected loads write nothing to standard output and one diagnostic line to standard error.
