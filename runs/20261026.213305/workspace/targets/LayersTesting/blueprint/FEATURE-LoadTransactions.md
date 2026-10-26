# FEATURE: Load Transactions

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger load transactions <csv>` with row validation and the final-balance rule, all or nothing. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-LoadAccounts.md, FEATURE-LoadCategories.md, FEATURE-Validation.md, FEATURE-BalanceRules.md, FEATURE-CsvOutput.md |
| Provides | ledger load transactions |
| Consumes | ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected |

## Purpose

`ledger load transactions <csv>` loads transaction records from a file whose header is exactly `txn_id,date,account,category,amount,memo`. Each loaded transaction keeps the `txn_id` from its file. The whole file is validated before the first write.

## Behavior

- Header must match exactly in names and order; otherwise exit 3 with no write.
- Each row is validated: `txn_id` is an integer, `date` a real calendar date `YYYY-MM-DD`, `account` and `category` valid codes that exist (stored rows), `amount` matching `-?DIGITS[.D[D]]` with at most two decimals and never zero (parsed to integer cents, no floating point), `memo` 0 to 60 characters without comma or newline.
- A `txn_id` repeated in the file or already stored rejects the file.
- The negative-balance rule is judged on each account's final balance after the whole file (stored balance plus all file amounts). An intermediate dip restored by a later row of the same file is accepted.
- Any failure exits 3 (unknown account or category, bad row, duplicate id, negative final balance), writes nothing to standard output and stores nothing.
- A header-only file loads zero rows and writes `table,loaded` then `transactions,0`.
- Success writes `table,loaded` then `transactions,<rows>`. Validation, the balance check and all inserts run in one database transaction.

## Database Interface

- `FEATURE-TXN-001` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-002` — read: get a transaction to detect a stored duplicate id - supplies: `txn_id` - returns: `txn_id`
- `FEATURE-TXN-003` — read: list an account's transactions for its stored balance - supplies: `account` - returns: `txn_id`, `account`, `amount`
- `FEATURE-ACCOUNT-002` — read: confirm an account exists - supplies: `account` - returns: `account`
- `FEATURE-CATEGORY-002` — read: confirm a category exists - supplies: `category` - returns: `category`

## Programmatic Acceptance

=== AC load-txn-success-keeps-ids ===
Intent: A valid file stores each row with its file txn_id and integer-cent amount, and reports the loaded count.

import csv
import io
import os
import tempfile
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZLT1A", "ZLT1C"
rows = [
    ["910001", "2026-05-01", acct, cat, "100.00", "first"],
    ["910002", "2026-05-02", acct, cat, "-25.50", "second"],
    ["910003", "2026-05-03", acct, cat, "7.05", ""],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Load txn")
    db.categories.create(category=cat, description="Load txn")
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.csv")
        with open(path, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(
                [["txn_id", "date", "account", "category", "amount", "memo"]] + rows
            )
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["table", "loaded"], ["transactions", str(len(rows))]]
    for r in rows:
        got = db.transactions.get(txn_id=int(r[0]))
        assert got is not None
        cents = int(Decimal(r[4]) * 100)
        assert (got.date, got.account, got.category, got.amount, got.memo) == (r[1], acct, cat, cents, r[5])
        assert isinstance(got.amount, int)
=== END AC load-txn-success-keeps-ids ===

=== AC load-txn-header-only ===
Intent: A file holding only its header loads zero rows and reports transactions,0.

import csv
import io
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.transactions.list())
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.csv")
        with open(path, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerow(
                ["txn_id", "date", "account", "category", "amount", "memo"]
            )
        code, out, err = cli_runner("load", "transactions", path)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["table", "loaded"], ["transactions", "0"]]
    assert len(db.transactions.list()) == before
=== END AC load-txn-header-only ===

=== AC load-txn-unknown-reference-atomic ===
Intent: An unknown account or category rejects the whole file with exit 3 and stores none of its rows.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZLT3A", "ZLT3C"
ghost_acct, ghost_cat = "ZLT3NOA", "ZLT3NOC"
good = [["910011", "2026-05-01", acct, cat, "10.00", "ok1"], ["910012", "2026-05-01", acct, cat, "10.00", "ok2"]]
with db_session() as db:
    db.accounts.create(account=acct, name="Ref test")
    db.categories.create(category=cat, description="Ref test")
    before = len(db.transactions.list())
    bad_rows = [
        ["910013", "2026-05-01", ghost_acct, cat, "10.00", "no account"],
        ["910013", "2026-05-01", acct, ghost_cat, "10.00", "no category"],
    ]
    for bad in bad_rows:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.csv")
            with open(path, "w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(
                    [["txn_id", "date", "account", "category", "amount", "memo"]] + good + [bad]
                )
            code, out, err = cli_runner("load", "transactions", path)
        print(code, out, err)
        assert code == 3
        assert out == ""
        for r in good:
            assert db.transactions.get(txn_id=int(r[0])) is None
    assert len(db.transactions.list()) == before
=== END AC load-txn-unknown-reference-atomic ===

=== AC load-txn-bad-field-rejected ===
Intent: Zero or over-precise amounts, impossible dates and invalid ids each reject the file with exit 3 and store nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZLT4A", "ZLT4C"
bad_variants = [
    ["910021", "2026-05-01", acct, cat, "0.00", "zero"],
    ["910021", "2026-05-01", acct, cat, "0", "zero"],
    ["910021", "2026-05-01", acct, cat, "-0", "zero"],
    ["910021", "2026-05-01", acct, cat, "1.234", "precision"],
    ["910021", "2026-05-01", acct, cat, ".50", "no leading digit"],
    ["910021", "2026-05-01", acct, cat, "+5.00", "plus sign"],
    ["910021", "2026-02-30", acct, cat, "5.00", "bad date"],
    ["910021", "2026-5-1", acct, cat, "5.00", "bad date format"],
    ["notanumber", "2026-05-01", acct, cat, "5.00", "bad id"],
    ["910021", "2026-05-01", acct, cat, "5.00", "m" * 61],
]
with db_session() as db:
    db.accounts.create(account=acct, name="Field test")
    db.categories.create(category=cat, description="Field test")
    before = len(db.transactions.list())
    for bad in bad_variants:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.csv")
            with open(path, "w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(
                    [["txn_id", "date", "account", "category", "amount", "memo"], bad]
                )
            code, out, err = cli_runner("load", "transactions", path)
        print(bad, code, out, err)
        assert code == 3
        assert out == ""
    assert db.transactions.get(txn_id=910021) is None
    assert len(db.transactions.list()) == before
=== END AC load-txn-bad-field-rejected ===

=== AC load-txn-duplicate-id ===
Intent: A txn_id repeated in the file or already stored rejects the file with exit 3.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZLT5A", "ZLT5C"
stored_id = 910031
fresh_id = 910032
with db_session() as db:
    db.accounts.create(account=acct, name="Dup test")
    db.categories.create(category=cat, description="Dup test")
    db.transactions.create(txn_id=stored_id, date="2026-05-01", account=acct, category=cat, amount=1000, memo="stored")
    before = len(db.transactions.list())
    cases = [
        [[str(fresh_id), "2026-05-02", acct, cat, "1.00", "a"], [str(fresh_id), "2026-05-02", acct, cat, "1.00", "b"]],
        [[str(fresh_id), "2026-05-02", acct, cat, "1.00", "a"], [str(stored_id), "2026-05-02", acct, cat, "1.00", "b"]],
    ]
    for rows in cases:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.csv")
            with open(path, "w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(
                    [["txn_id", "date", "account", "category", "amount", "memo"]] + rows
                )
            code, out, err = cli_runner("load", "transactions", path)
        print(code, out, err)
        assert code == 3
        assert out == ""
        assert db.transactions.get(txn_id=fresh_id) is None
        assert db.transactions.get(txn_id=stored_id).memo == "stored"
    assert len(db.transactions.list()) == before
=== END AC load-txn-duplicate-id ===

=== AC load-txn-final-balance-rule ===
Intent: The negative-balance rule is judged on the final balance of the whole file: a restored intermediate dip loads, a negative final balance is rejected with nothing stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZLT6A", "ZLT6C"
header = ["txn_id", "date", "account", "category", "amount", "memo"]


def run(rows):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.csv")
        with open(path, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows([header] + rows)
        return cli_runner("load", "transactions", path)


with db_session() as db:
    db.accounts.create(account=acct, name="Balance test")
    db.categories.create(category=cat, description="Balance test")

    negative = [
        ["910041", "2026-05-01", acct, cat, "50.00", "in"],
        ["910042", "2026-05-02", acct, cat, "-50.01", "too much out"],
    ]
    code, out, err = run(negative)
    print(code, out, err)
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=910041) is None
    assert db.transactions.get(txn_id=910042) is None

    dip_restored = [
        ["910043", "2026-05-01", acct, cat, "-100.00", "dip first"],
        ["910044", "2026-05-02", acct, cat, "200.00", "restore"],
    ]
    code, out, err = run(dip_restored)
    print(code, out, err)
    assert code == 0
    assert db.transactions.get(txn_id=910043).amount == -10000
    assert db.transactions.get(txn_id=910044).amount == 20000

    over_stored = [["910045", "2026-05-03", acct, cat, "-100.01", "past the stored balance"]]
    code, out, err = run(over_stored)
    print(code, out, err)
    assert code == 3
    assert db.transactions.get(txn_id=910045) is None

    within_stored = [["910046", "2026-05-03", acct, cat, "-100.00", "exactly to zero"]]
    code, out, err = run(within_stored)
    print(code, out, err)
    assert code == 0
    assert sum(r.amount for r in db.transactions.list(account=acct)) == 0
=== END AC load-txn-final-balance-rule ===

=== AC load-txn-seed-workflow ===
Intent: After init, the supplied seed files load in order, report their loaded counts, the rejected bad file changes nothing, and counts persist across invocations.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session


def data_rows(path):
    with open(path, newline="") as f:
        return len(list(csv.reader(f))) - 1


n_accounts = data_rows("sources/seed_accounts.csv")
n_categories = data_rows("sources/seed_categories.csv")
n_txns = data_rows("sources/seed_transactions.csv")

with db_session() as db:
    code, out, err = cli_runner("init")
    print(code, out, err)
    assert code == 0

    for table, path, n in (
        ("accounts", "sources/seed_accounts.csv", n_accounts),
        ("categories", "sources/seed_categories.csv", n_categories),
        ("transactions", "sources/seed_transactions.csv", n_txns),
    ):
        code, out, err = cli_runner("load", table, path)
        print(code, out, err)
        assert code == 0
        assert list(csv.reader(io.StringIO(out))) == [["table", "loaded"], [table, str(n)]]

    code, out, err = cli_runner("load", "transactions", "sources/seed_transactions_bad.csv")
    print(code, out, err)
    assert code == 3
    assert out == ""

    assert len(db.accounts.list()) == n_accounts
    assert len(db.categories.list()) == n_categories
    assert len(db.transactions.list()) == n_txns
=== END AC load-txn-seed-workflow ===

## User Acceptance

- None.

## Guardrails

- A rejected file stores no row and writes nothing to standard output.
- Amounts are parsed and stored as integer cents; no floating point at any layer.
- Application code never reads `sources/` seed files; they reach the database only through `ledger load`.
- Diagnostics go to standard error only and never include a DSN or credential.
