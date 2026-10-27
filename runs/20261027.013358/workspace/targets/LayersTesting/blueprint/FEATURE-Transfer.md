# FEATURE: Transfer

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Move cash between two accounts as a pair of TRANSFER transactions written atomically. |
| Depends On | FEATURE-LedgerRules.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-LoadCategories.md |
| Provides | ledger transfer |
| Consumes | ledgerlib.rules, ledgerlib.validation, ledgerlib.csvout |

## Purpose

`ledger transfer <from> <to> <amount> <date>` moves cash from one account to another. It stores
two rows in category `TRANSFER` with consecutive ids, or stores neither.

## Trigger

Command line: `./ledger transfer <from> <to> <amount> <date>`. Implemented in
`cli/commands/transfer.py` as `run(args) -> list[str]`.

## Sequence

1. Require exactly four arguments, else `UsageError` (exit 2) before any database access.
2. Validate both account codes, the amount and the date through `ledgerlib.validation`
   (exit 3 on violation). The amount must be strictly positive; zero and negative amounts are rejected.
3. Reject `<from>` equal to `<to>` (exit 3).
4. Open the ledger. Require both accounts and the category `TRANSFER` to exist (exit 3).
5. Project the source balance after the outgoing row with `ledgerlib.rules`; a negative result is
   rejected (exit 3). The destination balance only grows.
6. In one database transaction, read `next_txn_id`, write the outgoing row with that id, then the
   incoming row with the next id.
7. Return the header `txn_id,date,account,category,amount,memo` and both rows read back from storage.

## Rows Written

| Row | Account | Amount (cents) | Memo |
|-----|---------|----------------|------|
| Outgoing, id N | `<from>` | `-amount` | `transfer to <to>` |
| Incoming, id N+1 | `<to>` | `+amount` | `transfer from <from>` |

Both rows use category `TRANSFER` and the given date. Amounts are integer cents.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC transfer-success ===
Intent: A valid transfer exits 0, prints header plus two rows with consecutive ids, stores both rows, and conserves total cash.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

src = "ZZXFA1"
dst = "ZZXFB1"
seed_cat = "ZZXFSEED"
date = "2026-06-01"
amount = "50.00"
cents = int(Decimal(amount) * 100)
with db_session() as db:
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    db.categories.create(category=seed_cat, description="Xfer seed")
    db.accounts.create(account=src, name="Xfer Source")
    db.accounts.create(account=dst, name="Xfer Dest")
    seed_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=seed_id, date=date, account=src, category=seed_cat, amount=10000, memo="seed")
    total_before = sum(r.amount for r in db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, amount, date)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 3
    out_row, in_row = rows[1], rows[2]
    assert int(in_row[0]) == int(out_row[0]) + 1
    assert out_row[1] == date and in_row[1] == date
    assert out_row[2] == src and in_row[2] == dst
    assert out_row[3] == "TRANSFER" and in_row[3] == "TRANSFER"
    assert Decimal(out_row[4]) == Decimal(-cents) / 100
    assert Decimal(in_row[4]) == Decimal(cents) / 100
    first = db.transactions.get(txn_id=int(out_row[0]))
    second = db.transactions.get(txn_id=int(in_row[0]))
    assert first is not None and second is not None
    assert first.account == src and first.amount == -cents
    assert second.account == dst and second.amount == cents
    assert first.category == "TRANSFER" and second.category == "TRANSFER"
    assert sum(r.amount for r in db.transactions.list(account=src)) == 10000 - cents
    assert sum(r.amount for r in db.transactions.list(account=dst)) == cents
    assert sum(r.amount for r in db.transactions.list()) == total_before
=== END AC transfer-success ===

=== AC transfer-memo ===
Intent: The outgoing row memo names the destination and the incoming row memo names the source, as stored and as printed.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

src = "ZZXMA1"
dst = "ZZXMB1"
seed_cat = "ZZXMSEED"
date = "2026-06-02"
with db_session() as db:
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    db.categories.create(category=seed_cat, description="Xfer memo seed")
    db.accounts.create(account=src, name="Memo Source")
    db.accounts.create(account=dst, name="Memo Dest")
    seed_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=seed_id, date=date, account=src, category=seed_cat, amount=5000, memo="seed")
    code, out, err = cli_runner("transfer", src, dst, "10.00", date)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][5] == f"transfer to {dst}"
    assert rows[2][5] == f"transfer from {src}"
    assert db.transactions.get(txn_id=int(rows[1][0])).memo == rows[1][5]
    assert db.transactions.get(txn_id=int(rows[2][0])).memo == rows[2][5]
=== END AC transfer-memo ===

=== AC transfer-rejects-invalid ===
Intent: Non-positive or malformed amounts, equal accounts, unknown accounts and bad dates exit 3 with empty stdout and store nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

src = "ZZXRA1"
dst = "ZZXRB1"
seed_cat = "ZZXRSEED"
date = "2026-06-03"
with db_session() as db:
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    db.categories.create(category=seed_cat, description="Xfer reject seed")
    db.accounts.create(account=src, name="Reject Source")
    db.accounts.create(account=dst, name="Reject Dest")
    seed_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=seed_id, date=date, account=src, category=seed_cat, amount=100000, memo="seed")
    cases = [
        (src, dst, "0", date),
        (src, dst, "0.00", date),
        (src, dst, "-5.00", date),
        (src, dst, "1.234", date),
        (src, dst, "abc", date),
        (src, src, "5.00", date),
        (src, "ZZXRNONE", "5.00", date),
        ("ZZXRNONE", dst, "5.00", date),
        (src, dst, "5.00", "2026-02-30"),
        (src, dst, "5.00", "06/03/2026"),
    ]
    for args in cases:
        before = len(db.transactions.list())
        code, out, err = cli_runner("transfer", *args)
        print(args, code, out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC transfer-rejects-invalid ===

=== AC transfer-rejects-overdraft ===
Intent: A transfer exceeding the source balance by one cent exits 3 and leaves both balances and the row count unchanged; the exact balance succeeds.

from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

src = "ZZXOA1"
dst = "ZZXOB1"
seed_cat = "ZZXOSEED"
date = "2026-06-04"
balance_cents = 20000
with db_session() as db:
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    db.categories.create(category=seed_cat, description="Xfer overdraft seed")
    db.accounts.create(account=src, name="Overdraft Source")
    db.accounts.create(account=dst, name="Overdraft Dest")
    seed_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=seed_id, date=date, account=src, category=seed_cat, amount=balance_cents, memo="seed")
    too_much = str(Decimal(balance_cents + 1) / 100)
    exact = str(Decimal(balance_cents) / 100)
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, too_much, date)
    print(code, out, err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert sum(r.amount for r in db.transactions.list(account=src)) == balance_cents
    assert db.transactions.list(account=dst) == []
    code, out, err = cli_runner("transfer", src, dst, exact, date)
    print(code, out, err)
    assert code == 0
    assert sum(r.amount for r in db.transactions.list(account=src)) == 0
    assert sum(r.amount for r in db.transactions.list(account=dst)) == balance_cents
=== END AC transfer-rejects-overdraft ===

=== AC transfer-usage ===
Intent: A transfer with the wrong argument count exits 2 with empty stdout and writes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    before = len(db.transactions.list())
    for args in [(), ("A",), ("A", "B"), ("A", "B", "1.00"), ("A", "B", "1.00", "2026-01-01", "extra")]:
        code, out, err = cli_runner("transfer", *args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC transfer-usage ===

## User Acceptance

- None.

## Guardrails

- Every check completes before the first write; a rejected transfer stores neither row.
- Both rows are written in one database transaction.
- Amounts are integer cents; no floating point at any layer.
- Diagnostics go to standard error only; a failing transfer writes nothing to standard output.
