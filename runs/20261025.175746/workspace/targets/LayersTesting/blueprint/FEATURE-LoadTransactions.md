# FEATURE: Load Transactions

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Implements `ledger load transactions <csv>` keeping file txn_ids, with all-or-nothing validation and balance checking. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md |
| Provides    | ledger load transactions |
| Consumes    | transactions.create, transactions.get, accounts.get, categories.get, check_balances |

## Purpose

Bulk-load transactions from a CSV file whose header is exactly
`txn_id,date,account,category,amount,memo`. Each loaded row keeps the `txn_id` from its file. The
command checks every row and the resulting balances before its first write.

## Trigger

`./ledger load transactions <csv>`

## Sequence

1. Reject a wrong argument count with exit 2.
2. Read the file. An unreadable file exits 1.
3. Require the exact header; any other header exits 3.
4. Validate every row: `txn_id` is an integer; the date is a real calendar date `YYYY-MM-DD`; the
   amount matches `-?DIGITS[.D[D]]`, has at most two decimals, and is never zero; the memo is 0 to
   60 characters with no comma or newline. Amounts are parsed to integer cents without floating point.
5. Reject (exit 3) a `txn_id` repeated within the file or already stored, an account absent from
   `accounts`, and a category absent from `categories`.
6. Apply the whole file to the stored balances through `check_balances`; if any account balance
   would be below zero after the file is applied, exit 3 (Decision Q-004: final balances are checked).
7. Only then write all rows through `transactions.create`, keeping each file `txn_id`.
8. Print `table,loaded` and `transactions,<rows>`.

A failing command writes nothing to standard output and one diagnostic line to standard error.

## Reads

- `transactions.get`, `accounts.get`, `categories.get` for validation; stored transactions via `check_balances`.

## Writes

- `transactions.create` once per validated row, after all validation has passed.

## Database Interface

- `FEATURE-TRANSACTIONS-001` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-002` — read: find a stored transaction by id - supplies: `txn_id` - returns: `txn_id`, `account`, `amount`
- `FEATURE-ACCOUNTS-002` — read: find a stored account by code - supplies: `account` - returns: `account`
- `FEATURE-CATEGORIES-002` — read: find a stored category by code - supplies: `category` - returns: `category`

## Programmatic Acceptance

=== AC load-transactions-valid ===
Intent: A valid transactions file keeps its txn_ids, stores integer cents, and reports the loaded count.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def dollars(c):
    return ("-" if c < 0 else "") + str(abs(c) // 100) + "." + format(abs(c) % 100, "02d")

acct = "UTMA1"
cat = "UTMC1"
rows = [
    (910001, "2026-05-01", 10000, "opening"),
    (910002, "2026-05-02", -2550, "spend"),
    (910007, "2026-05-03", 475, "gap id kept"),
]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "txns.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        for txn_id, when, cents, memo in rows:
            w.writerow([txn_id, when, acct, cat, dollars(cents), memo])
    with db_session() as db:
        db.accounts.create(account=acct, name="Load Txn")
        db.categories.create(category=cat, description="Load Txn")
        code, out, err = cli_runner("load", "transactions", path)
        print(out)
        print(err)
        assert code == 0
        parsed = list(csv.reader(io.StringIO(out)))
        assert parsed == [["table", "loaded"], ["transactions", str(len(rows))]]
        for txn_id, when, cents, memo in rows:
            stored = db.transactions.get(txn_id=txn_id)
            assert stored is not None
            assert stored.date == when
            assert stored.account == acct
            assert stored.category == cat
            assert stored.amount == cents
            assert isinstance(stored.amount, int)
            assert stored.memo == memo
=== END AC load-transactions-valid ===

=== AC load-transactions-unknown-references ===
Intent: An unknown account or unknown category in the last row exits 3 and stores none of the preceding valid rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTMB1"
cat = "UTMD1"
first_id = 910101
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.accounts.create(account=acct, name="Refs")
        db.categories.create(category=cat, description="Refs")
        variants = [
            ("UTMBNONE", cat, 910102),
            (acct, "UTMDNONE", 910103),
        ]
        for index, (bad_acct, bad_cat, bad_id) in enumerate(variants):
            path = os.path.join(tmp, f"refs{index}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
                w.writerow([first_id, "2026-05-01", acct, cat, "10.00", "ok"])
                w.writerow([bad_id, "2026-05-01", bad_acct, bad_cat, "10.00", "bad"])
            code, out, err = cli_runner("load", "transactions", path)
            print(err)
            assert code == 3
            assert out == ""
            assert db.transactions.get(txn_id=first_id) is None
            assert db.transactions.get(txn_id=bad_id) is None
=== END AC load-transactions-unknown-references ===

=== AC load-transactions-field-rules ===
Intent: An impossible date, a third decimal place, a zero amount, and a non-integer id each reject the whole file with exit 3.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTME1"
cat = "UTME2"
anchor_id = 910201
bad_rows = [
    [910202, "2026-02-30", acct, cat, "1.00", "bad date"],
    [910203, "2026-05-01", acct, cat, "1.234", "three decimals"],
    [910204, "2026-05-01", acct, cat, "0.00", "zero"],
    ["abc", "2026-05-01", acct, cat, "1.00", "bad id"],
]
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.accounts.create(account=acct, name="Fields")
        db.categories.create(category=cat, description="Fields")
        for index, bad in enumerate(bad_rows):
            path = os.path.join(tmp, f"fields{index}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
                w.writerow([anchor_id, "2026-05-01", acct, cat, "5.00", "anchor"])
                w.writerow(bad)
            code, out, err = cli_runner("load", "transactions", path)
            print(err)
            assert code == 3
            assert out == ""
            assert db.transactions.get(txn_id=anchor_id) is None
=== END AC load-transactions-field-rules ===

=== AC load-transactions-duplicate-ids ===
Intent: A txn_id repeated in the file or already stored rejects the whole file with exit 3 and changes nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTMF1"
cat = "UTMF2"
stored_id = 910301
fresh_id = 910302
repeated = 910303
stored_cents = 5000
with tempfile.TemporaryDirectory() as tmp:
    with db_session() as db:
        db.accounts.create(account=acct, name="Dups")
        db.categories.create(category=cat, description="Dups")
        db.transactions.create(
            txn_id=stored_id, date="2026-05-01", account=acct, category=cat,
            amount=stored_cents, memo="stored",
        )
        against_store = os.path.join(tmp, "store.csv")
        with open(against_store, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerow([fresh_id, "2026-05-02", acct, cat, "1.00", "fresh"])
            w.writerow([stored_id, "2026-05-02", acct, cat, "1.00", "clash"])
        code, out, err = cli_runner("load", "transactions", against_store)
        print(err)
        assert code == 3 and out == ""
        assert db.transactions.get(txn_id=fresh_id) is None
        assert db.transactions.get(txn_id=stored_id).amount == stored_cents

        within = os.path.join(tmp, "within.csv")
        with open(within, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerow([repeated, "2026-05-02", acct, cat, "1.00", "one"])
            w.writerow([repeated, "2026-05-02", acct, cat, "2.00", "two"])
        code, out, err = cli_runner("load", "transactions", within)
        print(err)
        assert code == 3 and out == ""
        assert db.transactions.get(txn_id=repeated) is None
=== END AC load-transactions-duplicate-ids ===

=== AC load-transactions-negative-balance ===
Intent: A file that would leave an account balance below zero exits 3 and stores none of its rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "UTMG1"
other = "UTMG2"
cat = "UTMG3"
ok_id = 910401
overdraw_id = 910402
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "overdraw.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
        w.writerow([ok_id, "2026-05-01", other, cat, "100.00", "fine"])
        w.writerow([overdraw_id, "2026-05-01", acct, cat, "-0.01", "overdraw"])
    with db_session() as db:
        db.accounts.create(account=acct, name="Empty")
        db.accounts.create(account=other, name="Other")
        db.categories.create(category=cat, description="Bal")
        code, out, err = cli_runner("load", "transactions", path)
        print(err)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=ok_id) is None
        assert db.transactions.get(txn_id=overdraw_id) is None
=== END AC load-transactions-negative-balance ===

=== AC load-transactions-header-and-usage ===
Intent: A mismatched header exits 3, a missing file exits 1, and a missing file argument exits 2.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as tmp:
    wrong = os.path.join(tmp, "wrong.csv")
    with open(wrong, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["account", "name"])
        w.writerow(["UTMH1", "Wrong Header"])
    missing = os.path.join(tmp, "absent.csv")
    with db_session():
        code, out, err = cli_runner("load", "transactions", wrong)
        assert code == 3 and out == ""
        code, out, err = cli_runner("load", "transactions", missing)
        assert code == 1 and out == ""
        code, out, err = cli_runner("load", "transactions")
        assert code == 2 and out == ""
=== END AC load-transactions-header-and-usage ===

## User Acceptance

- None.

## Guardrails

- Validate every row, every reference, and the resulting balances before the first write.
- Amounts are integer cents; no floating point at any layer.
- A loaded transaction keeps the `txn_id` from its file.
- Do not read `sources/` seed files from application code.
- Diagnostics go to standard error only and are never compared.
