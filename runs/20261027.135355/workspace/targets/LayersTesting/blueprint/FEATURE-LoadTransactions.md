# FEATURE: Load Transactions

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger load transactions <csv>` with full validation and the balance rule checked before any write. |
| Depends On | FEATURE-LoadCsvReader.md, FEATURE-Validation.md, FEATURE-BalanceRule.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, DATABASE.md |
| Provides | ledger load transactions |
| Consumes | ledger_core.csvio, ledger_core.validation, ledger_core.balances, cli.registry |

## Purpose

Load transactions from a CSV file whose header is `txn_id,date,account,category,amount,memo`.
Each row keeps the `txn_id` from the file. The file is accepted entirely or not at all.

## Behavior

1. `ledger load transactions <csv>` takes exactly one file argument; other counts exit 2.
2. Read the file with `ledger_core.csvio.read_rows(path, ("txn_id", "date", "account", "category", "amount", "memo"))`.
   An unreadable file exits 1; a wrong header or wrong field count exits 3.
3. Validate every row before any write: `txn_id` is an integer, not repeated in the file and not
   already stored; the date is a real calendar date `YYYY-MM-DD`; the account and category exist in
   the store; the amount matches `-?DIGITS[.D[D]]`, has at most two decimals, and is not zero; the
   memo is 0 to 60 characters with no comma or newline. Amounts are converted to integer cents
   without floating point.
4. Apply `ledger_core.balances.check_no_negative` to all rows together as inserts. The effect of
   the whole file is considered at once, so a withdrawal that precedes its funding deposit in the
   file is accepted when the final balance is not below zero. A resulting negative balance for any
   account rejects the file.
5. Insert every row in one atomic unit, then print `table,loaded` and `transactions,<rows>`.
6. Any rejection exits 3, writes nothing to standard output, and stores none of the rows.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: confirm each referenced account exists - supplies: `account` - returns: `account`
- `FEATURE-CATEGORY-002` — read: confirm each referenced category exists - supplies: `category` - returns: `category`
- `FEATURE-TXN-002` — read: detect an already stored txn_id - supplies: `txn_id` - returns: `txn_id`
- `FEATURE-TXN-001` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC load-transactions-success ===
Intent: a valid file loads every row keeping its txn_id, prints the declared two CSV rows, and each stored row reads back with the cents derived from the input text.
Requires: executable=python3; scope=test

import csv
import io
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMA1", "ZZMC1"
rows = [
    ["920000001", "2026-01-02", acct, cat, "100.50", "deposit"],
    ["920000002", "2026-01-03", acct, cat, "-20.25", "withdrawal"],
    ["920000003", "2026-01-04", acct, cat, "7", ""],
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "txns.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["transactions", str(len(rows))]]
        for tid, day, a, c, amt, memo in rows:
            row = db.transactions.get(txn_id=int(tid))
            assert row is not None
            g = (lambda n: row[n]) if isinstance(row, dict) else (lambda n: getattr(row, n))
            assert g("date") == day
            assert g("account") == a
            assert g("category") == c
            assert g("amount") == int(Decimal(amt) * 100)
            assert g("memo") == memo
=== END AC load-transactions-success ===

=== AC load-transactions-unknown-reference-stores-nothing ===
Intent: a final row naming an unknown account rejects the whole file with exit 3, and none of the ten valid rows before it is stored.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMB1", "ZZMC2"
base = 920000100
good = [[str(base + i), "2026-04-01", acct, cat, "10.00", "bad batch %d" % i] for i in range(1, 11)]
bad = [str(base + 11), "2026-04-01", "ZZNOSUCH", cat, "10.00", "unknown account"]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "txns.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerows(good)
        w.writerow(bad)
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        code, out, err = cli_runner("load", "transactions", path)
        assert code == 3
        assert out == ""
        for r in good:
            assert db.transactions.get(txn_id=int(r[0])) is None
        assert db.transactions.get(txn_id=int(bad[0])) is None

        unknown_cat = [[str(base + 20), "2026-04-01", acct, "ZZNOCAT", "10.00", ""]]
        path2 = os.path.join(d, "txns2.csv")
        with open(path2, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerows(unknown_cat)
        code, out, err = cli_runner("load", "transactions", path2)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=base + 20) is None
=== END AC load-transactions-unknown-reference-stores-nothing ===

=== AC load-transactions-invalid-fields ===
Intent: each invalid date, amount, memo, or txn_id rejects the file with exit 3 and stores neither the bad row nor the valid row before it.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMC1", "ZZMC3"
first_id = 920000200
first = [str(first_id), "2026-05-01", acct, cat, "10.00", "ok"]
bad_rows = [
    ["920000201", "2026-02-30", acct, cat, "10.00", "impossible date"],
    ["920000202", "2026-5-1", acct, cat, "10.00", "short date"],
    ["920000203", "2026-05-01", acct, cat, "1.234", "three decimals"],
    ["920000204", "2026-05-01", acct, cat, "0.00", "zero amount"],
    ["920000205", "2026-05-01", acct, cat, "abc", "not a number"],
    ["920000206", "2026-05-01", acct, cat, "10.00", "m" * 61],
    ["notanumber", "2026-05-01", acct, cat, "10.00", "bad id"],
]
with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        for i, bad in enumerate(bad_rows):
            path = os.path.join(d, "t%d.csv" % i)
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
                w.writerow(first)
                w.writerow(bad)
            code, out, err = cli_runner("load", "transactions", path)
            assert code == 3, bad
            assert out == ""
            assert db.transactions.get(txn_id=first_id) is None
=== END AC load-transactions-invalid-fields ===

=== AC load-transactions-duplicate-ids-rejected ===
Intent: a txn_id repeated inside the file, or already stored, rejects the whole file with exit 3 and leaves the stored row unchanged.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMD1", "ZZMC4"
head = ["txn_id", "date", "account", "category", "amount", "memo"]

def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(head)
        w.writerows(rows)

with tempfile.TemporaryDirectory() as d:
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        p1 = os.path.join(d, "dup_in_file.csv")
        write(p1, [["920000300", "2026-06-01", acct, cat, "5.00", ""],
                   ["920000300", "2026-06-02", acct, cat, "6.00", ""]])
        code, out, err = cli_runner("load", "transactions", p1)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=920000300) is None

        stored_id = 920000310
        stored_cents = 4321
        db.transactions.create(txn_id=stored_id, date="2026-06-03", account=acct,
                               category=cat, amount=stored_cents, memo="stored")
        p2 = os.path.join(d, "dup_stored.csv")
        write(p2, [["920000311", "2026-06-04", acct, cat, "1.00", ""],
                   [str(stored_id), "2026-06-05", acct, cat, "9.99", "replacement"]])
        code, out, err = cli_runner("load", "transactions", p2)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=920000311) is None
        row = db.transactions.get(txn_id=stored_id)
        got = row["amount"] if isinstance(row, dict) else row.amount
        assert got == stored_cents
=== END AC load-transactions-duplicate-ids-rejected ===

=== AC load-transactions-negative-balance-rejected ===
Intent: a file whose combined effect leaves an account below zero is rejected with exit 3 and stores no row, even though each row is individually well formed.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZME1", "ZZMC5"
head = ["txn_id", "date", "account", "category", "amount", "memo"]
rows = [
    ["920000400", "2026-07-01", acct, cat, "1.00", "deposit"],
    ["920000401", "2026-07-02", acct, cat, "-2.00", "overdraw"],
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "txns.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(head)
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        code, out, err = cli_runner("load", "transactions", path)
        assert code == 3
        assert out == ""
        for r in rows:
            assert db.transactions.get(txn_id=int(r[0])) is None
        assert db.transactions.list(account=acct) == []
=== END AC load-transactions-negative-balance-rejected ===

=== AC load-transactions-balance-considers-whole-file ===
Intent: a withdrawal listed before the deposit that funds it is accepted because the balance rule uses the combined effect of all rows, and both rows are stored.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMF1", "ZZMC6"
head = ["txn_id", "date", "account", "category", "amount", "memo"]
rows = [
    ["920000500", "2026-08-01", acct, cat, "-3.00", "withdraw first"],
    ["920000501", "2026-08-02", acct, cat, "5.00", "deposit second"],
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "txns.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(head)
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 0
        stored = db.transactions.list(account=acct)
        total = sum((r["amount"] if isinstance(r, dict) else r.amount) for r in stored)
        assert total == sum(int(Decimal(r[4]) * 100) for r in rows)
        assert len(stored) == len(rows)
=== END AC load-transactions-balance-considers-whole-file ===

=== AC load-transactions-header-and-usage ===
Intent: a wrong header exits 3 with nothing stored, an unreadable file exits 1, and a missing file argument exits 2.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZZMG1", "ZZMC7"
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "wrong_header.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "date", "account", "category", "amount", "memo"])
        w.writerow(["920000600", "2026-09-01", acct, cat, "1.00", ""])
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn Account")
        db.categories.create(category=cat, description="Load Txn Category")
        code, out, err = cli_runner("load", "transactions", path)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=920000600) is None
        code, out, err = cli_runner("load", "transactions", os.path.join(d, "missing.csv"))
        assert code == 1
        assert out == ""
        code, out, err = cli_runner("load", "transactions")
        assert code == 2
        assert out == ""
=== END AC load-transactions-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- No row is written until every row has passed validation and the balance rule.
- Amounts are integer cents; floating point is never used for money.
- The file's `txn_id` values are kept; none is renumbered.
- A failing command writes nothing to standard output.
