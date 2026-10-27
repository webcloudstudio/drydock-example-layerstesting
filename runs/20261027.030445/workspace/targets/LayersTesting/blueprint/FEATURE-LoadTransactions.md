# FEATURE: Load Transactions

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The transactions loader with amount, date, memo, reference, and non-negative balance validation, plus the shared validators later stories reuse. |
| Depends On | FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger load transactions |
| Consumes | ledger load, accounts, categories, transactions |

## Purpose

Register `transactions` with the shared load dispatcher. Each stored transaction keeps the `txn_id`
from its file. This story also provides the shared validators `parse_amount`, `validate_date`,
`validate_memo`, and a balance check that `txn post`, `txn amend`, `txn delete`, and `transfer`
import.

## Behavior

- The header must be `txn_id,date,account,category,amount,memo`; a mismatch exits 3.
- `txn_id` is an integer. A duplicate id inside the file, or one already stored, is rejected.
- Amounts match `-?DIGITS[.D[D]]`: at most two decimal places and never zero. They are converted to
  integer cents by string and integer arithmetic only; floating point is never used.
- Dates are real Gregorian calendar dates written `YYYY-MM-DD`; February 29 is valid only in a leap
  year and `2026-02-30` is rejected.
- Memos are 0 to 60 characters with no comma or newline.
- Each row's account and category must exist in the store.
- The balance rule (Plan decision Q-002): for every account the batch touches, the stored balance plus
  the sum of the batch's amounts for that account must not be below zero. The final balance is
  checked, so file order within the batch does not matter.
- Everything is checked before the first write. Any failure exits 3, writes nothing to standard
  output, and stores none of the rows. Success stores all rows in one transaction and writes
  `table,loaded` then `transactions,<rows>`.
- Loading the staged accounts, categories, and transactions seed files in that order into an empty
  ledger accepts 4, 7, and 120 rows.

## Database Interface

- `FEATURE-TXN-001` — write: store a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-002` — read: detect an existing transaction id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-005` — read: sum stored amounts per account - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORY-002` — read: confirm the category exists - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC load-transactions-success ===
Intent: A valid file for existing accounts and categories exits 0, reports the count, keeps each file txn_id, and stores amounts as integer cents.

import csv
import io
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX01"
cat = "ZQX01"
rows = [
    ["910001", "2026-05-01", acct, cat, "100.50", "first"],
    ["910002", "2026-05-02", acct, cat, "-20.25", ""],
]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn")
        db.categories.create(category=cat, description="Load Txn")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["transactions", str(len(rows))]]
        for r in rows:
            stored = db.transactions.get(txn_id=int(r[0]))
            assert stored is not None
            assert stored.date == r[1]
            assert stored.account == r[2]
            assert stored.category == r[3]
            assert stored.amount == int(Decimal(r[4]) * 100)
            assert stored.memo == r[5]
=== END AC load-transactions-success ===

=== AC load-transactions-final-balance ===
Intent: A debit that precedes its funding credit in the same file is accepted because only each account's final balance must be non-negative.

import csv
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX02"
cat = "ZQX02"
rows = [
    ["910011", "2026-05-01", acct, cat, "-10.00", "debit first"],
    ["910012", "2026-05-01", acct, cat, "25.00", "credit second"],
]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=acct, name="Balance")
        db.categories.create(category=cat, description="Balance")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 0
        total = sum(t.amount for t in db.transactions.list(account=acct))
        assert total == sum(int(Decimal(r[4]) * 100) for r in rows)
=== END AC load-transactions-final-balance ===

=== AC load-transactions-negative-balance ===
Intent: A batch whose final balance for an account is below zero is rejected with exit 3 and none of the batch is stored, including rows for other accounts.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

funded = "ZQX03"
poor = "ZQX04"
cat = "ZQX03"
rows = [
    ["910021", "2026-05-01", funded, cat, "50.00", "ok"],
    ["910022", "2026-05-01", poor, cat, "-0.01", "overdraw"],
]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerows(rows)
    with db_session() as db:
        db.accounts.create(account=funded, name="Funded")
        db.accounts.create(account=poor, name="Poor")
        db.categories.create(category=cat, description="Neg")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 3
        assert out == ""
        for r in rows:
            assert db.transactions.get(txn_id=int(r[0])) is None
=== END AC load-transactions-negative-balance ===

=== AC load-transactions-stored-balance ===
Intent: The balance rule includes rows already stored: a debit larger than the stored balance is rejected with nothing stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX05"
cat = "ZQX05"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerow(["910032", "2026-05-02", acct, cat, "-10.01", "too much"])
    with db_session() as db:
        db.accounts.create(account=acct, name="Stored")
        db.categories.create(category=cat, description="Stored")
        db.transactions.create(
            txn_id=910031, date="2026-05-01", account=acct, category=cat, amount=1000, memo=""
        )
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=910032) is None
=== END AC load-transactions-stored-balance ===

=== AC load-transactions-rejections-atomic ===
Intent: Each rule violation placed after a valid row exits 3 with empty stdout and leaves the valid row unstored; cases cover unknown account, unknown category, 3-decimal amount, zero amount, non-numeric amount, impossible date, non-leap Feb 29, over-long memo, comma memo, and bad txn_id.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX06"
cat = "ZQX06"
good = ["910041", "2026-05-01", acct, cat, "10.00", "good"]
bad_rows = [
    ["910042", "2026-05-01", "ZQNOACCT", cat, "1.00", ""],
    ["910042", "2026-05-01", acct, "ZQNOCAT", "1.00", ""],
    ["910042", "2026-05-01", acct, cat, "1.234", ""],
    ["910042", "2026-05-01", acct, cat, "0.00", ""],
    ["910042", "2026-05-01", acct, cat, "abc", ""],
    ["910042", "2026-02-30", acct, cat, "1.00", ""],
    ["910042", "2026-02-29", acct, cat, "1.00", ""],
    ["910042", "2026-05-01", acct, cat, "1.00", "M" * 61],
    ["910042", "2026-05-01", acct, cat, "1.00", "a,b"],
    ["notanint", "2026-05-01", acct, cat, "1.00", ""],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.accounts.create(account=acct, name="Reject")
        db.categories.create(category=cat, description="Reject")
        before = len(db.transactions.list())
        for i, bad in enumerate(bad_rows):
            path = os.path.join(tmp, "t%d.csv" % i)
            with open(path, "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
                w.writerow(good)
                w.writerow(bad)
            code, out, err = cli_runner("load", "transactions", path)
            print(i, code, out, err)
            assert code == 3
            assert out == ""
            assert db.transactions.get(txn_id=int(good[0])) is None
            assert len(db.transactions.list()) == before
=== END AC load-transactions-rejections-atomic ===

=== AC load-transactions-leap-day ===
Intent: February 29 is accepted in a Gregorian leap year (2028) and the row is stored with that date.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX07"
cat = "ZQX07"
leap = "2028-02-29"
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerow(["910051", leap, acct, cat, "5.00", ""])
    with db_session() as db:
        db.accounts.create(account=acct, name="Leap")
        db.categories.create(category=cat, description="Leap")
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 0
        assert db.transactions.get(txn_id=910051).date == leap
=== END AC load-transactions-leap-day ===

=== AC load-transactions-duplicate-ids ===
Intent: A txn_id repeated in the file, or already stored, rejects the whole file with exit 3 and stores nothing new.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQX08"
cat = "ZQX08"
header = ["txn_id", "date", "account", "category", "amount", "memo"]
with tempfile.TemporaryDirectory() as tmp:
    in_file = os.path.join(tmp, "a.csv")
    with open(in_file, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerow(["910061", "2026-05-01", acct, cat, "5.00", ""])
        w.writerow(["910061", "2026-05-02", acct, cat, "6.00", ""])
    vs_stored = os.path.join(tmp, "b.csv")
    with open(vs_stored, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerow(["910063", "2026-05-01", acct, cat, "5.00", ""])
        w.writerow(["910062", "2026-05-02", acct, cat, "6.00", ""])
    with db_session() as db:
        db.accounts.create(account=acct, name="Dup")
        db.categories.create(category=cat, description="Dup")
        db.transactions.create(
            txn_id=910062, date="2026-05-01", account=acct, category=cat, amount=100, memo=""
        )
        before = len(db.transactions.list())
        code, out, err = cli_runner("load", "transactions", in_file)
        assert code == 3
        assert out == ""
        code, out, err = cli_runner("load", "transactions", vs_stored)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
        assert db.transactions.get(txn_id=910061) is None
        assert db.transactions.get(txn_id=910063) is None
=== END AC load-transactions-duplicate-ids ===

=== AC load-transactions-header-mismatch ===
Intent: A transactions file whose header omits a column is rejected with exit 3 and nothing stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "t.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount"])
        w.writerow(["910071", "2026-05-01", "ZQX09", "ZQX09", "1.00"])
    with db_session() as db:
        before = len(db.transactions.list())
        code, out, err = cli_runner("load", "transactions", path)
        print(out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC load-transactions-header-mismatch ===

=== AC load-transactions-seed-files ===
Intent: Loading the supplied accounts, categories, and transactions seed files in order into an emptied ledger reports 4, 7, and 120 rows and retains them.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

expected = [("accounts", 4), ("categories", 7), ("transactions", 120)]
with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    db.categories.delete_all(min_category="")
    db.accounts.delete_all(min_account="")
    for table, n in expected:
        code, out, err = cli_runner("load", table, "sources/seed_%s.csv" % table)
        print(table, code, out, err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], [table, str(n)]]
    assert len(db.accounts.list()) == 4
    assert len(db.categories.list()) == 7
    assert len(db.transactions.list()) == 120
=== END AC load-transactions-seed-files ===

## User Acceptance

- None.

## Guardrails

- Money is integer cents at every layer; no floating point in parsing, summing, or formatting.
- A rejected load changes no stored record.
- Application code never reads a seed file or `sources/run.sh`; seed files arrive only through this command.
- Persistence is reached only through the `persistence` package.
