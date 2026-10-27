# FEATURE: Transfer

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger transfer <from> <to> <amount> <date>`, an atomic two-row move of cash between distinct accounts in category TRANSFER. |
| Depends On | FEATURE-TxnPost.md, FEATURE-Validation.md, FEATURE-BalanceRule.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger transfer |
| Consumes | ledger_core.transactions, ledger_core.validation, ledger_core.balances, cli.registry |

## Purpose

Move cash between two accounts as two transaction rows that are stored together or not at all. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

## Behavior

1. Argument count other than four after `transfer` exits 2.
2. Validate before any write: the amount is positive with at most two decimals, the date is a real `YYYY-MM-DD` date, both accounts exist, they differ, and category `TRANSFER` exists. Any violation exits 3.
3. The source balance after the debit must not be below zero, checked through `ledger_core.balances`; otherwise exit 3.
4. The outgoing row takes id max(txn_id)+1 (or 1 when empty): amount `-amount`, account `<from>`, category `TRANSFER`, memo `transfer to <to>`. The incoming row takes the next id: amount `+amount`, account `<to>`, memo `transfer from <from>`.
5. Both rows are inserted atomically and printed under the header `txn_id,date,account,category,amount,memo`.
6. A failing command writes nothing to standard output and stores neither row.

## Database Interface

- None — persistence is owned by DATABASE.md and reached through `ledger_core.transactions`.

## Programmatic Acceptance

=== AC transfer-success ===
Intent: A valid transfer exits 0 and prints two rows with consecutive ids starting at the previous maximum plus one, category TRANSFER, the signed amounts, and the specified memos; a separate read shows both stored.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

src, dst, cat = "ZZTF1", "ZZTF2", "TRANSFER"
day = "2026-05-10"
amount_text = "250.00"
cents = int(amount_text.replace(".", ""))
with db_session() as db:
    db.accounts.create(account=src, name="Source Account")
    db.accounts.create(account=dst, name="Dest Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Internal transfer")
    db.transactions.create(txn_id=900300001, date="2026-05-01", account=src, category=cat, amount=100000, memo="funding")
    before_max = max(f(r, "txn_id") for r in db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, amount_text, day)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 3
    out_row, in_row = rows[1], rows[2]
    assert int(out_row[0]) == before_max + 1
    assert int(in_row[0]) == int(out_row[0]) + 1
    assert out_row[1] == day and in_row[1] == day
    assert out_row[2] == src and in_row[2] == dst
    assert out_row[3] == cat and in_row[3] == cat
    assert out_row[4] == "-" + amount_text
    assert in_row[4] == amount_text
    assert out_row[5] == "transfer to " + dst
    assert in_row[5] == "transfer from " + src
    assert f(db.transactions.get(txn_id=int(out_row[0])), "amount") == -cents
    assert f(db.transactions.get(txn_id=int(in_row[0])), "amount") == cents
=== END AC transfer-success ===

=== AC transfer-conserves-cash ===
Intent: A valid transfer moves cash without changing the total held by the two accounts, computed from stored rows before and after.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

src, dst, cat = "ZZTF3", "ZZTF4", "TRANSFER"
with db_session() as db:
    db.accounts.create(account=src, name="Source Account")
    db.accounts.create(account=dst, name="Dest Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Internal transfer")
    db.transactions.create(txn_id=900300010, date="2026-05-01", account=src, category=cat, amount=50000, memo="funding")

    def balance(code_):
        return sum(f(r, "amount") for r in db.transactions.list(account=code_))

    src_before, dst_before = balance(src), balance(dst)
    code, out, err = cli_runner("transfer", src, dst, "123.45", "2026-05-11")
    print(out)
    print(err)
    assert code == 0
    assert balance(src) + balance(dst) == src_before + dst_before
    assert balance(src) == src_before - 12345
    assert balance(dst) == dst_before + 12345
=== END AC transfer-conserves-cash ===

=== AC transfer-insufficient-funds ===
Intent: A transfer exceeding the source balance by one cent exits 3 and stores neither row; a transfer of exactly the balance then succeeds and leaves the source at zero.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

src, dst, cat = "ZZTF5", "ZZTF6", "TRANSFER"
with db_session() as db:
    db.accounts.create(account=src, name="Source Account")
    db.accounts.create(account=dst, name="Dest Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Internal transfer")
    db.transactions.create(txn_id=900300020, date="2026-05-01", account=src, category=cat, amount=10000, memo="funding")
    total_before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "100.01", "2026-05-12")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == total_before
    assert db.transactions.list(account=dst) == []
    code, out, err = cli_runner("transfer", src, dst, "100.00", "2026-05-12")
    print(out)
    print(err)
    assert code == 0
    assert sum(f(r, "amount") for r in db.transactions.list(account=src)) == 0
=== END AC transfer-insufficient-funds ===

=== AC transfer-rejections ===
Intent: Same source and destination, zero or negative amounts, three decimals, an impossible date, and an unknown account are each rejected with exit 3, with empty stdout and no new rows.

from cli.testing import cli_runner
from persistence.testing import db_session

src, dst, cat = "ZZTF7", "ZZTF8", "TRANSFER"
missing = "ZZTFNONE"
with db_session() as db:
    db.accounts.create(account=src, name="Source Account")
    db.accounts.create(account=dst, name="Dest Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Internal transfer")
    db.transactions.create(txn_id=900300030, date="2026-05-01", account=src, category=cat, amount=100000, memo="funding")
    assert db.accounts.get(account=missing) is None
    total_before = len(db.transactions.list())
    cases = [
        (src, src, "5.00", "2026-05-13"),
        (src, dst, "0", "2026-05-13"),
        (src, dst, "-5.00", "2026-05-13"),
        (src, dst, "5.001", "2026-05-13"),
        (src, dst, "5.00", "2026-02-30"),
        (src, missing, "5.00", "2026-05-13"),
        (missing, dst, "5.00", "2026-05-13"),
    ]
    for args in cases:
        code, out, err = cli_runner("transfer", *args)
        print(args, code, out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == total_before
=== END AC transfer-rejections ===

=== AC transfer-usage ===
Intent: A wrong argument count for transfer exits 2 with nothing on stdout.

from cli.testing import cli_runner

for args in [("transfer",), ("transfer", "A", "B", "1.00"), ("transfer", "A", "B", "1.00", "2026-05-01", "extra")]:
    code, out, err = cli_runner(*args)
    print(out)
    print(err)
    assert code == 2
    assert out == ""
=== END AC transfer-usage ===

## User Acceptance

- None.

## Guardrails

- Both rows are written together or neither is; every check runs before the first write.
- Amounts are integer cents; floating point is never used for money.
- Standard output stays empty on any failure; the diagnostic goes to standard error.
- Ids are never hardcoded; they derive from the largest stored `txn_id`.
