# FEATURE: Load Transactions

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger load transactions <csv>` with whole-file validation and whole-file balance checking. |
| Depends On | FEATURE-LoadCategories.md, FEATURE-LedgerRules.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger load transactions |
| Consumes | ledger load categories, ledgerlib.rules, ledgerlib.validation |

## Purpose

Bulk load transactions, keeping each file's `txn_id`, so that either every row is stored or none is.

## Interface

`ledger load transactions <csv>` adds the `transactions` handler to `cli/commands/load.py`.

Output on success:

```text
table,loaded
transactions,<rows>
```

## Behavior

1. An unreadable file is exit 1 with nothing on stdout.
2. The header must be exactly `txn_id,date,account,category,amount,memo`, else exit 3.
3. Each row has the header's field count, else exit 3.
4. `txn_id` is a string of decimal digits; each row keeps its file `txn_id`. A `txn_id` repeated in the file or already stored is rejected (exit 3).
5. `date` is a real calendar date `YYYY-MM-DD`. `amount` matches `-?DIGITS[.D[D]]`, at most two decimals, never zero, and is converted to integer cents with integer arithmetic. `memo` is 0 to 60 characters with no comma or newline.
6. `account` must be stored and `category` must be stored, else exit 3.
7. The balance rule is evaluated on each affected account's final balance after the whole file is applied on top of the stored transactions, not row by row. Any final balance below zero rejects the whole file (exit 3).
8. Every check precedes the first write; writes happen in one database transaction. A rejected file changes nothing.
9. A header-only file loads zero rows and prints `transactions,0`.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC load-txn-success ===
Intent: A valid file loads every row keeping its file txn_id, reports the count, and each row reads back with cents derived from the input text.

import csv
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA1"
cat = "ZZLTC1"
rows = [
    ["880001", "2026-04-01", acct, cat, "100.00", "first"],
    ["880002", "2026-04-02", acct, cat, "-30.25", "second"],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn A")
    db.categories.create(category=cat, description="Load Txn Cat")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "t.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerows(rows)
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed == [["table", "loaded"], ["transactions", str(len(rows))]]
    for tid, date, a, c, amount, memo in rows:
        row = db.transactions.get(txn_id=int(tid))
        assert row is not None
        assert row.date == date
        assert row.account == a
        assert row.category == c
        assert row.amount == int(Decimal(amount) * 100)
        assert row.memo == memo
=== END AC load-txn-success ===

=== AC load-txn-final-balance-rule ===
Intent: The balance rule uses each account's balance after the whole file, so a withdrawal listed before the deposit that covers it is accepted.

import csv
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA2"
cat = "ZZLTC2"
rows = [
    ["880011", "2026-04-01", acct, cat, "-50.00", "out first"],
    ["880012", "2026-04-01", acct, cat, "100.00", "in second"],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn B")
    db.categories.create(category=cat, description="Load Txn Cat2")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "t.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerows(rows)
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 0
    stored = db.transactions.list(account=acct)
    assert sum(r.amount for r in stored) == sum(int(Decimal(r[4]) * 100) for r in rows)
=== END AC load-txn-final-balance-rule ===

=== AC load-txn-negative-final-balance ===
Intent: A file that leaves an account below zero is rejected with exit 3 and none of its rows, including valid ones, are stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA3"
cat = "ZZLTC3"
rows = [
    ["880021", "2026-04-01", acct, cat, "10.00", "in"],
    ["880022", "2026-04-02", acct, cat, "-20.00", "out"],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn C")
    db.categories.create(category=cat, description="Load Txn Cat3")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "t.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerows(rows)
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 3
    assert out == ""
    for r in rows:
        assert db.transactions.get(txn_id=int(r[0])) is None
=== END AC load-txn-negative-final-balance ===

=== AC load-txn-stored-balance-counts ===
Intent: The balance check includes already stored transactions, so a withdrawal exceeding the stored balance is rejected with exit 3 and the stored data is unchanged.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA4"
cat = "ZZLTC4"
stored_id = 880031
new_id = 880032
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn D")
    db.categories.create(category=cat, description="Load Txn Cat4")
    db.transactions.create(
        txn_id=stored_id, date="2026-04-01", account=acct, category=cat, amount=5000, memo="stored"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "t.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerow([str(new_id), "2026-04-02", acct, cat, "-60.00", "too much"])
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 3
    assert db.transactions.get(txn_id=new_id) is None
    assert len(db.transactions.list(account=acct)) == 1
=== END AC load-txn-stored-balance-counts ===

=== AC load-txn-unknown-references ===
Intent: A row naming an unknown account or an unknown category rejects the whole file with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA5"
cat = "ZZLTC5"
good_id = 880041
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn E")
    db.categories.create(category=cat, description="Load Txn Cat5")
    variants = [
        ["880042", "2026-04-02", "ZZNOACCT", cat, "5.00", "unknown account"],
        ["880043", "2026-04-02", acct, "ZZNOCAT", "5.00", "unknown category"],
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for i, bad in enumerate(variants):
            path = os.path.join(tmp, f"u{i}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
                w.writerow([str(good_id), "2026-04-01", acct, cat, "5.00", "valid"])
                w.writerow(bad)
            code, out, err = cli_runner("load", "transactions", path)
            print(code, out, err)
            assert code == 3
            assert out == ""
            assert db.transactions.get(txn_id=good_id) is None
            assert db.transactions.get(txn_id=int(bad[0])) is None
=== END AC load-txn-unknown-references ===

=== AC load-txn-duplicate-ids ===
Intent: A txn_id repeated in the file, or already stored, is rejected with exit 3 and the stored row is unchanged.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA6"
cat = "ZZLTC6"
stored_id = 880051
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn F")
    db.categories.create(category=cat, description="Load Txn Cat6")
    db.transactions.create(
        txn_id=stored_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo="stored"
    )
    with tempfile.TemporaryDirectory() as tmp:
        p1 = os.path.join(tmp, "a.csv")
        with open(p1, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerow(["880052", "2026-04-02", acct, cat, "1.00", "one"])
            w.writerow(["880052", "2026-04-02", acct, cat, "2.00", "two"])
        code1, out1, err1 = cli_runner("load", "transactions", p1)
        p2 = os.path.join(tmp, "b.csv")
        with open(p2, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["txn_id", "date", "account", "category", "amount", "memo"])
            w.writerow([str(stored_id), "2026-04-03", acct, cat, "9.00", "clash"])
        code2, out2, err2 = cli_runner("load", "transactions", p2)
    print(out1, err1, out2, err2)
    assert code1 == 3
    assert code2 == 3
    assert db.transactions.get(txn_id=880052) is None
    kept = db.transactions.get(txn_id=stored_id)
    assert kept is not None
    assert kept.amount == 1000
    assert kept.memo == "stored"
=== END AC load-txn-duplicate-ids ===

=== AC load-txn-invalid-fields ===
Intent: An impossible date, a three-decimal amount, a zero amount, and a non-numeric id are each rejected with exit 3 and store nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA7"
cat = "ZZLTC7"
header = ["txn_id", "date", "account", "category", "amount", "memo"]
cases = [
    ["880061", "2026-02-30", acct, cat, "1.00", "bad date"],
    ["880062", "2026-04-01", acct, cat, "1.234", "bad amount"],
    ["880063", "2026-04-01", acct, cat, "0.00", "zero amount"],
    ["abc", "2026-04-01", acct, cat, "1.00", "bad id"],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn G")
    db.categories.create(category=cat, description="Load Txn Cat7")
    with tempfile.TemporaryDirectory() as tmp:
        for i, row in enumerate(cases):
            path = os.path.join(tmp, f"c{i}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(header)
                w.writerow(row)
            code, out, err = cli_runner("load", "transactions", path)
            print(row, code, out, err)
            assert code == 3
            assert out == ""
    assert db.transactions.list(account=acct) == []
=== END AC load-txn-invalid-fields ===

=== AC load-txn-header-and-field-count ===
Intent: A wrong header and a short data row are each rejected with exit 3 and store nothing; a header-only file loads zero rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZLTA8"
cat = "ZZLTC8"
header = ["txn_id", "date", "account", "category", "amount", "memo"]
with db_session() as db:
    db.accounts.create(account=acct, name="Load Txn H")
    db.categories.create(category=cat, description="Load Txn Cat8")
    with tempfile.TemporaryDirectory() as tmp:
        p1 = os.path.join(tmp, "h.csv")
        with open(p1, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["id", "date", "account", "category", "amount", "memo"])
            w.writerow(["880071", "2026-04-01", acct, cat, "1.00", "x"])
        code1, out1, err1 = cli_runner("load", "transactions", p1)
        p2 = os.path.join(tmp, "s.csv")
        with open(p2, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            w.writerow(["880072", "2026-04-01", acct, cat, "1.00", "x"])
            w.writerow(["880073", "2026-04-01", acct])
        code2, out2, err2 = cli_runner("load", "transactions", p2)
        p3 = os.path.join(tmp, "e.csv")
        with open(p3, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerow(header)
        code3, out3, err3 = cli_runner("load", "transactions", p3)
    print(out1, err1, out2, err2, out3, err3)
    assert code1 == 3
    assert code2 == 3
    assert code3 == 0
    assert list(csv.reader(out3.splitlines())) == [["table", "loaded"], ["transactions", "0"]]
    assert db.transactions.list(account=acct) == []
=== END AC load-txn-header-and-field-count ===

=== AC load-txn-unreadable-file ===
Intent: An unreadable path is an operational failure with exit 1 and nothing on standard output.

import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = cli_runner("load", "transactions", os.path.join(tmp, "missing.csv"))
    print(out, err)
    assert code == 1
    assert out == ""
=== END AC load-txn-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- A rejected load stores none of the file's rows and changes no stored row.
- The balance rule is evaluated once per account on the final balance after the whole file.
- Amounts are integer cents; no floating point at any layer.
- Application code never reads `sources/seed_transactions.csv` or `sources/run.sh`.
- Diagnostics go to standard error only.
