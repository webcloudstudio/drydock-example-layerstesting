# FEATURE: Load Transactions

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger load transactions <csv>`, which loads transactions keeping their file ids, all-or-nothing. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md |
| Provides | ledger load transactions |
| Consumes | cli.main, parse_amount, validate_text, validate_date, balance_guard, ledger load accounts, ledger load categories |

## Purpose

Bulk-load transaction rows. Each loaded transaction keeps the `txn_id` written in its file. The
command either stores every row or stores nothing.

## Command Contract

`ledger load transactions <csv>` registers under the `load` command in the cli command table.

| Condition | Result |
|---|---|
| File readable, header equals `txn_id,date,account,category,amount,memo`, every row valid, resulting balances non-negative | Exit 0. Stdout is `table,loaded` then `transactions,<rows>`. |
| Missing `<csv>` argument or extra arguments | Exit 2, nothing on stdout. |
| File missing or unreadable | Exit 1, nothing on stdout. |
| Header mismatch; non-integer `txn_id`; bad date, amount, or memo | Exit 3, nothing stored. |
| Unknown account or unknown category | Exit 3, nothing stored. |
| A `txn_id` repeats within the file or already exists in the table | Exit 3, nothing stored. |
| Loading would leave any account balance below zero | Exit 3, nothing stored. |

## Behavior

1. Read the whole file with the standard `csv` module and check the header.
2. For each row validate the id, the date (a real calendar date), the amount (`-?DIGITS[.D[D]]`,
   never zero, parsed to integer cents), the memo (0 to 60 characters, no comma or newline), and
   that the account and category exist.
3. Reject repeated ids within the file and ids already stored.
4. Compute each touched account's stored balance plus the file's amounts with `balance_guard`; any
   result below zero rejects the file.
5. Only after every check passes, write all rows in one transaction, then print the result.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: confirm every named account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORY-002` — read: confirm every named category exists - supplies: `category` - returns: `category`, `description`
- `FEATURE-TXN-002` — read: read existing ids and balances - supplies: `account`, `category` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

Rows are written through `db.transactions.create`, the operation declared for the post feature in
`DATABASE.md`; this feature reuses it and declares no operation of its own.

## Programmatic Acceptance

=== AC load-transactions-valid ===
Intent: A valid transactions file keeps its file ids, reports the loaded count, and every row reads back.

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

def load(table, header, rows, tmp):
    path = os.path.join(tmp, table + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

acct, cat = "LDTXA1", "LDTXC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
ids = [base + 1, base + 2, base + 3]
rows = [
    [ids[0], "2026-05-01", acct, cat, "100.00", "deposit"],
    [ids[1], "2026-05-02", acct, cat, "-25.50", "payment"],
    [ids[2], "2026-05-03", acct, cat, "10.25", ""],
]
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Load Txn Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Load Txn Category"]], tmp)[0] == 0
    before = counts()
    rc, out, err = load(
        "transactions", ["txn_id", "date", "account", "category", "amount", "memo"], rows, tmp
    )
print(out)
print(err)
assert rc == 0
parsed = list(csv.reader(io.StringIO(out)))
assert parsed == [["table", "loaded"], ["transactions", str(len(rows))]]
assert counts()["transactions"] == before["transactions"] + len(rows)
cents = [10000, -2550, 1025]
with db_session() as db:
    for row, c in zip(rows, cents):
        got = db.transactions.get(txn_id=row[0])
        assert got is not None
        assert got.date == row[1]
        assert got.account == acct
        assert got.category == cat
        assert got.amount == c
        assert got.memo == row[5]
=== END AC load-transactions-valid ===

=== AC load-transactions-unknown-references ===
Intent: An unknown account or unknown category rejects the file with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def load(table, header, rows, tmp, name=None):
    path = os.path.join(tmp, (name or table) + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

header = ["txn_id", "date", "account", "category", "amount", "memo"]
acct, cat = "LDURA1", "LDURC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Ref Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Ref Category"]], tmp)[0] == 0
    bad_account = [
        [base + 1, "2026-05-01", acct, cat, "50.00", "ok"],
        [base + 2, "2026-05-01", "LDNOACCT", cat, "5.00", "bad"],
    ]
    rc, out, err = load("transactions", header, bad_account, tmp, "a")
    print(out, err)
    assert rc == 3
    assert out == ""
    bad_category = [
        [base + 3, "2026-05-01", acct, cat, "50.00", "ok"],
        [base + 4, "2026-05-01", acct, "LDNOCAT", "5.00", "bad"],
    ]
    rc, out, err = load("transactions", header, bad_category, tmp, "b")
    print(out, err)
    assert rc == 3
    assert out == ""
with db_session() as db:
    for i in (1, 2, 3, 4):
        assert db.transactions.get(txn_id=base + i) is None
=== END AC load-transactions-unknown-references ===

=== AC load-transactions-invalid-fields ===
Intent: A bad amount, zero amount, bad calendar date, or bad memo each reject the file with exit 3 and store nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def load(table, header, rows, tmp, name=None):
    path = os.path.join(tmp, (name or table) + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

header = ["txn_id", "date", "account", "category", "amount", "memo"]
acct, cat = "LDIFA1", "LDIFC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
cases = [
    ("2026-05-01", "1.234", "three decimals"),
    ("2026-05-01", "0.00", "zero amount"),
    ("2026-02-30", "5.00", "impossible date"),
    ("2026-05-01", "5.00", "m" * 61),
]
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Field Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Field Category"]], tmp)[0] == 0
    for n, (day, amount, memo) in enumerate(cases, start=1):
        rc, out, err = load(
            "transactions", header, [[base + n, day, acct, cat, amount, memo]], tmp, "t%d" % n
        )
        print(n, out, err)
        assert rc == 3
        assert out == ""
with db_session() as db:
    for n in range(1, len(cases) + 1):
        assert db.transactions.get(txn_id=base + n) is None
=== END AC load-transactions-invalid-fields ===

=== AC load-transactions-duplicate-ids ===
Intent: A txn_id repeated in the file, or already stored, rejects the file with exit 3 and adds nothing.

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
acct, cat = "LDDIA1", "LDDIC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Dup Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Dup Category"]], tmp)[0] == 0
    before = counts()
    twice = [
        [base + 1, "2026-05-01", acct, cat, "10.00", "a"],
        [base + 1, "2026-05-02", acct, cat, "10.00", "b"],
    ]
    rc, out, err = load("transactions", header, twice, tmp, "twice")
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == before

    once = [[base + 2, "2026-05-03", acct, cat, "10.00", "c"]]
    rc, out, err = load("transactions", header, once, tmp, "once")
    assert rc == 0
    after_first = counts()
    rc, out, err = load("transactions", header, once, tmp, "once")
    print(out, err)
    assert rc == 3
    assert out == ""
    assert counts() == after_first
=== END AC load-transactions-duplicate-ids ===

=== AC load-transactions-negative-balance ===
Intent: A file that would leave an account balance below zero is rejected with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def load(table, header, rows, tmp, name=None):
    path = os.path.join(tmp, (name or table) + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return cli_runner("load", table, path)

header = ["txn_id", "date", "account", "category", "amount", "memo"]
acct, cat = "LDNBA1", "LDNBC1"
with db_session() as db:
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1000
rows = [
    [base + 1, "2026-05-01", acct, cat, "20.00", "deposit"],
    [base + 2, "2026-05-02", acct, cat, "-20.01", "overdraw"],
]
with tempfile.TemporaryDirectory() as tmp:
    assert load("accounts", ["account", "name"], [[acct, "Balance Account"]], tmp)[0] == 0
    assert load("categories", ["category", "description"], [[cat, "Balance Category"]], tmp)[0] == 0
    rc, out, err = load("transactions", header, rows, tmp, "overdraw")
print(out, err)
assert rc == 3
assert out == ""
with db_session() as db:
    assert db.transactions.get(txn_id=base + 1) is None
    assert db.transactions.get(txn_id=base + 2) is None
=== END AC load-transactions-negative-balance ===

=== AC load-transactions-usage-and-io ===
Intent: A missing argument is a usage error (exit 2) and an unreadable file is an operational failure (exit 1).

import os
import tempfile
from cli.testing import cli_runner

rc, out, err = cli_runner("load", "transactions")
print(out, err)
assert rc == 2
assert out == ""

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.csv")
    rc, out, err = cli_runner("load", "transactions", missing)
print(out, err)
assert rc == 1
assert out == ""
=== END AC load-transactions-usage-and-io ===

## User Acceptance

- None.

## Guardrails

- A loaded transaction keeps the `txn_id` from its file; no id is reassigned.
- Amounts are parsed to integer cents; no floating point is used at any layer.
- Every check, including the projected balances, completes before the first write.
- Application code never reads `sources/` seed files; the file path comes only from the command line.
