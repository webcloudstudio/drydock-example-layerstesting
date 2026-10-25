# FEATURE: Transfer

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger transfer <from> <to> <amount> <date>`, writing two TRANSFER rows atomically. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCore.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger transfer |
| Consumes | cli.main, parse_amount, format_amount, validate_date, balance_guard |

## Purpose

Move cash between two accounts as a pair of transactions in category `TRANSFER`. Both rows are stored or neither is.

## Trigger and Interface

`ledger transfer <from> <to> <amount> <date>` takes exactly four arguments.

| Condition | Exit | Stdout |
|-----------|------|--------|
| Transferred | 0 | Header `txn_id,date,account,category,amount,memo`, then the outgoing row, then the incoming row |
| Amount malformed, zero, or negative; date invalid; `from` equals `to`; either account unknown | 3 | Nothing |
| Amount exceeds the balance of `from` | 3 | Nothing |
| Wrong argument count | 2 | Nothing |
| Database unreachable or tables missing | 1 | Nothing |

One diagnostic line goes to standard error on every failure.

## Rows Written

| Row | Id | Account | Amount | Memo |
|-----|----|---------|--------|------|
| Outgoing | one more than the largest `txn_id` present, or 1 in an empty table | `<from>` | `-amount` | `transfer to <to>` |
| Incoming | the outgoing id plus one | `<to>` | `+amount` | `transfer from <from>` |

Both rows use category `TRANSFER` and the given date.

## Sequence

1. Check the argument count (usage error otherwise).
2. Parse the amount into integer cents; it must be positive. Validate the date. Require `from` and `to` to differ.
3. Confirm both accounts exist by listing accounts.
4. List transactions; compute the next id and the balance of `from`. Ask `balance_guard` whether subtracting the amount leaves `from` at or above zero.
5. Only after every check passes, write both rows in one database session, outgoing first. The writes use the transaction insert declared by FEATURE-TxnPost.md. A failure of either write leaves neither row stored.
6. Print the header and the two rows.

## Reads

Both accounts, and all transactions for the next id and the source balance.

## Writes

Two `transactions` rows, or none.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: confirm both accounts exist - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: list transactions for the next id and the source balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC transfer-success ===
Intent: A valid transfer prints two TRANSFER rows with consecutive ids and stores both.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "XFSRC1"
    dst = "XFDST1"
    day = "2026-04-03"
    opening = "OPENX1"
    db.accounts.create(account=src, name="Transfer Source")
    db.accounts.create(account=dst, name="Transfer Dest")
    db.categories.create(category=opening, description="Opening")
    db.categories.create(category="TRANSFER", description="Internal transfer") if db.categories.get(category="TRANSFER") is None else None
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-04-01", account=src, category=opening, amount=10000, memo="fund")
    code, out, err = cli_runner("transfer", src, dst, "25.00", day)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 3
    out_row, in_row = rows[1], rows[2]
    assert out_row[:5] == [str(base + 2), day, src, "TRANSFER", "-25.00"]
    assert in_row[:5] == [str(base + 3), day, dst, "TRANSFER", "25.00"]
    assert out_row[5].split(" ") == ["transfer", "to", dst]
    assert in_row[5].split(" ") == ["transfer", "from", src]
    stored_out = db.transactions.get(txn_id=base + 2)
    stored_in = db.transactions.get(txn_id=base + 3)
    assert stored_out is not None and stored_in is not None
    assert stored_out.amount == -2500 and stored_out.account == src
    assert stored_in.amount == 2500 and stored_in.account == dst
=== END AC transfer-success ===

=== AC transfer-balances ===
Intent: A transfer moves exactly the amount between the two account balances.

from persistence.testing import db_session
from cli.testing import cli_runner

def balance(db, account):
    return sum(t.amount for t in db.transactions.list(account=account))

with db_session() as db:
    src = "XFSRC2"
    dst = "XFDST2"
    opening = "OPENX2"
    db.accounts.create(account=src, name="Balance Source")
    db.accounts.create(account=dst, name="Balance Dest")
    db.categories.create(category=opening, description="Opening")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-04-01", account=src, category=opening, amount=10000, memo="fund")
    src_before = balance(db, src)
    dst_before = balance(db, dst)
    code, out, err = cli_runner("transfer", src, dst, "40.00", "2026-04-03")
    print(out)
    print(err)
    assert code == 0
    assert balance(db, src) == src_before - 4000
    assert balance(db, dst) == dst_before + 4000
=== END AC transfer-balances ===

=== AC transfer-entire-balance ===
Intent: Transferring the entire source balance leaves it at zero and is accepted.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "XFSRC3"
    dst = "XFDST3"
    opening = "OPENX3"
    db.accounts.create(account=src, name="Boundary Source")
    db.accounts.create(account=dst, name="Boundary Dest")
    db.categories.create(category=opening, description="Opening")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-04-01", account=src, category=opening, amount=10000, memo="fund")
    code, out, err = cli_runner("transfer", src, dst, "100.00", "2026-04-03")
    print(out)
    print(err)
    assert code == 0
    assert sum(t.amount for t in db.transactions.list(account=src)) == 0
    assert sum(t.amount for t in db.transactions.list(account=dst)) == 10000
=== END AC transfer-entire-balance ===

=== AC transfer-rejected-writes-nothing ===
Intent: Non-positive amounts, identical accounts, unknown accounts, bad dates, and malformed amounts exit 3 and write no row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "XFSRC4"
    dst = "XFDST4"
    opening = "OPENX4"
    db.accounts.create(account=src, name="Reject Source")
    db.accounts.create(account=dst, name="Reject Dest")
    db.categories.create(category=opening, description="Opening")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-04-01", account=src, category=opening, amount=10000, memo="fund")
    before = len(db.transactions.list())
    cases = [
        (src, dst, "0", "2026-04-03"),
        (src, dst, "0.00", "2026-04-03"),
        (src, dst, "-5.00", "2026-04-03"),
        (src, dst, "1.234", "2026-04-03"),
        (src, dst, "abc", "2026-04-03"),
        (src, src, "5.00", "2026-04-03"),
        (src, "XFNONE", "5.00", "2026-04-03"),
        ("XFNONE", dst, "5.00", "2026-04-03"),
        (src, dst, "5.00", "2026-02-30"),
    ]
    for args in cases:
        code, out, err = cli_runner("transfer", *args)
        print(args, code, out, err)
        assert code == 3
        assert out == ""
        assert len(db.transactions.list()) == before
=== END AC transfer-rejected-writes-nothing ===

=== AC transfer-overdraw ===
Intent: A transfer larger than the source balance exits 3 and writes neither row.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    src = "XFSRC5"
    dst = "XFDST5"
    opening = "OPENX5"
    db.accounts.create(account=src, name="Overdraw Source")
    db.accounts.create(account=dst, name="Overdraw Dest")
    db.categories.create(category=opening, description="Opening")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-04-01", account=src, category=opening, amount=10000, memo="fund")
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", src, dst, "100.01", "2026-04-03")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
    assert db.transactions.get(txn_id=base + 2) is None
=== END AC transfer-overdraw ===

=== AC transfer-usage ===
Intent: Wrong argument counts are usage errors with exit 2 and no output.

from cli.testing import cli_runner

for args in (
    ("transfer",),
    ("transfer", "A", "B", "1.00"),
    ("transfer", "A", "B", "1.00", "2026-04-03", "extra"),
):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC transfer-usage ===

## User Acceptance

- None.

## Guardrails

- Both rows are stored or neither; every check completes before the first write.
- The outgoing row takes the next id and the incoming row the id after it.
- Amounts are integer cents at every layer; no floating point.
- The source account balance never goes below zero.
- Standard output carries only the documented CSV; failures write one diagnostic line to standard error and nothing to standard output.
- Only the generated persistence package reaches the database.
