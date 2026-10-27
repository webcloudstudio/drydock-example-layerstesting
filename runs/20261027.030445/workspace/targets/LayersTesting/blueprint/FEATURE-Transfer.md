# FEATURE: Transfer

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger transfer`, which records an equal debit and credit in category TRANSFER as one all-or-nothing change. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger transfer |
| Consumes | ledger, accounts, categories, transactions |

## Purpose

Move cash between two distinct accounts. Both transaction rows are stored or neither is, and total cash held never changes.

## Interface

`ledger transfer <from> <to> <amount> <date>`

| Outcome | Exit | Standard output |
|---------|------|-----------------|
| Transferred | 0 | header `txn_id,date,account,category,amount,memo`, then the outgoing row, then the incoming row |
| Any rule violated | 3 | nothing |

## Behavior

1. Validate before any write: both accounts exist (an unknown account is exit 3), the accounts differ, the amount matches `DIGITS[.D[D]]` and is strictly positive, the date is a real Gregorian calendar date, category `TRANSFER` exists (otherwise exit 3, it is not created implicitly), and the source balance after the debit is not below zero.
2. Let `n` be one more than the largest stored `txn_id`, or 1 when empty. Store the outgoing row with id `n`: account `<from>`, category `TRANSFER`, amount `-amount`, memo naming `<to>` as `transfer to <to>`.
3. Store the incoming row with id `n+1`: account `<to>`, category `TRANSFER`, amount `+amount`, memo `transfer from <from>`.
4. Both writes happen in one persistence-library transaction so a failure leaves neither row.
5. Write the header and the two rows with amounts at exactly two decimals.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC transfer-success-two-rows ===
Intent: A valid transfer exits 0, returns the outgoing then incoming row with consecutive ids in category TRANSFER and equal opposite amounts, persists both, and conserves total cash.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

src = "ZQF1"
dst = "ZQF2"
fund_cat = "ZQFC"
amount_text = "100.00"
date = "2026-06-10"
cents = int(Decimal(amount_text) * 100)
funding = 50000
with db_session() as db:
    db.accounts.create(account=src, name="Source")
    db.accounts.create(account=dst, name="Dest")
    db.categories.create(category=fund_cat, description="Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=src, category=fund_cat, amount=funding, memo="")
    nxt = base + 1
    code, out, err = cli_runner("transfer", src, dst, amount_text, date)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 3
    out_row, in_row = rows[1], rows[2]
    assert int(out_row[0]) == nxt
    assert int(in_row[0]) == nxt + 1
    assert out_row[1] == date and in_row[1] == date
    assert out_row[2] == src and in_row[2] == dst
    assert out_row[3] == "TRANSFER" and in_row[3] == "TRANSFER"
    assert Decimal(out_row[4]) == -Decimal(amount_text)
    assert Decimal(in_row[4]) == Decimal(amount_text)
    assert re.fullmatch(r"-?\d+\.\d{2}", out_row[4])
    assert re.fullmatch(r"-?\d+\.\d{2}", in_row[4])
    assert dst in out_row[5]
    assert src in in_row[5]
    stored_out = db.transactions.get(txn_id=nxt)
    stored_in = db.transactions.get(txn_id=nxt + 1)
    assert stored_out is not None and stored_in is not None
    assert stored_out.amount == -cents and stored_in.amount == cents
    assert stored_out.memo == out_row[5] and stored_in.memo == in_row[5]
    src_bal = sum(t.amount for t in db.transactions.list(account=src))
    dst_bal = sum(t.amount for t in db.transactions.list(account=dst))
    assert src_bal == funding - cents
    assert dst_bal == cents
    assert src_bal + dst_bal == funding
=== END AC transfer-success-two-rows ===

=== AC transfer-rejects-insufficient-funds ===
Intent: A transfer larger than the source balance exits 3, prints nothing, and stores neither row.

from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

src = "ZQF3"
dst = "ZQF4"
fund_cat = "ZQFD"
amount_text = "50.01"
funding = 5000
assert int(Decimal(amount_text) * 100) > funding
with db_session() as db:
    db.accounts.create(account=src, name="Source")
    db.accounts.create(account=dst, name="Dest")
    db.categories.create(category=fund_cat, description="Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=src, category=fund_cat, amount=funding, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, amount_text, "2026-06-11")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert db.transactions.list(account=dst) == []
=== END AC transfer-rejects-insufficient-funds ===

=== AC transfer-rejects-invalid-requests ===
Intent: Identical accounts, a zero amount, a negative amount, a more-than-two-decimal amount, an impossible date, and an unknown account each exit 3 with empty output and no stored row.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "ZQF5"
dst = "ZQF6"
missing = "ZQNOPE"
fund_cat = "ZQFE"
with db_session() as db:
    db.accounts.create(account=src, name="Source")
    db.accounts.create(account=dst, name="Dest")
    db.categories.create(category=fund_cat, description="Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=src, category=fund_cat, amount=100000, memo="")
    before = len(db.transactions.list())
    attempts = [
        (src, src, "10.00", "2026-06-12"),
        (src, dst, "0.00", "2026-06-12"),
        (src, dst, "-5.00", "2026-06-12"),
        (src, dst, "1.234", "2026-06-12"),
        (src, dst, "10.00", "2026-02-30"),
        (src, missing, "10.00", "2026-06-12"),
        (missing, dst, "10.00", "2026-06-12"),
    ]
    for args in attempts:
        code, out, err = cli_runner("transfer", *args)
        print(args, code)
        print(err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC transfer-rejects-invalid-requests ===

=== AC transfer-leap-day ===
Intent: February 29 is accepted in a Gregorian leap year and rejected in a non-leap year.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "ZQF7"
dst = "ZQF8"
fund_cat = "ZQFF"
leap_date = "2028-02-29"
common_date = "2027-02-29"
with db_session() as db:
    db.accounts.create(account=src, name="Source")
    db.accounts.create(account=dst, name="Dest")
    db.categories.create(category=fund_cat, description="Funding")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account=src, category=fund_cat, amount=100000, memo="")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "5.00", common_date)
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    code, out, err = cli_runner("transfer", src, dst, "5.00", leap_date)
    print(out)
    print(err)
    assert code == 0
    assert len(db.transactions.list()) == before + 2
=== END AC transfer-leap-day ===

## User Acceptance

- None.

## Guardrails

- A rejected transfer stores neither row.
- Category `TRANSFER` is never created implicitly.
- Amounts are integer cents; no floating point.
- Only the persistence package is used to reach the store.
