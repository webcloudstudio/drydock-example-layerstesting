# FEATURE: Transfer

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `ledger transfer` command moves cash between two distinct accounts by storing two matching TRANSFER rows, both or neither. |
| Depends On  | FEATURE-BalanceRules.md, FEATURE-CliFoundation.md, DATABASE.md |
| Provides    | ledger transfer |
| Consumes    | transactions.create, transactions.list, accounts.get, check_balances |

## Purpose

`ledger transfer <from> <to> <amount> <date>` records an equal debit on the source account and credit on the destination account in category `TRANSFER`, so total cash held is unchanged.

## Trigger

An operator runs `./ledger transfer` with four arguments.

## Sequence

1. Reject a wrong argument count with exit 2.
2. Validate both account codes, the amount, and the date. The accounts must differ, the amount must be positive with at most two decimals, and the date must be a real calendar date. Any violation exits 3.
3. Look up both accounts with `accounts.get`. An unknown account exits 3.
4. List the source account's transactions and run `check_balances` with the proposed debit and credit. A balance below zero exits 3.
5. Compute `n` as the largest stored `txn_id` plus one (or `1` when none exist).
6. Store the outgoing row (`-amount`, source account, id `n`, memo `transfer to <to>`) and the incoming row (`+amount`, destination account, id `n+1`, memo `transfer from <from>`), both in category `TRANSFER`, both as one unit of work: both are stored or neither.
7. Print the header row and both rows, outgoing first. Exit 0.

## Output

```text
txn_id,date,account,category,amount,memo
<n>,<date>,<from>,TRANSFER,-<amount>,transfer to <to>
<n+1>,<date>,<to>,TRANSFER,<amount>,transfer from <from>
```

## Reads

- `accounts.get`, `transactions.list`

## Writes

- `transactions.create` twice, only after every check has passed

## Database Interface

- `FEATURE-TRANSACTIONS-001` — write: create the outgoing and incoming rows - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-003` — read: list transactions to find the largest id and the source balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNTS-002` — read: confirm each account exists - supplies: `account` - returns: `account`, `name`

## Programmatic Acceptance

=== AC transfer-valid ===
Intent: A valid transfer prints two consecutive-id TRANSFER rows with opposite amounts and stores both.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

src = "TRFSRC1"
dst = "TRFDST1"
amount_text = "250.00"
when = "2026-04-03"
with db_session() as db:
    db.accounts.create(account=src, name="Transfer Source")
    db.accounts.create(account=dst, name="Transfer Destination")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    if db.categories.get(category="TRFOPEN") is None:
        db.categories.create(category="TRFOPEN", description="Transfer opening")
    first = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=first, date="2026-04-01", account=src, category="TRFOPEN", amount=100000, memo="fund"
    )
    before_max = first
    code, out, err = cli_runner("transfer", src, dst, amount_text, when)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 3
    out_row, in_row = rows[1], rows[2]
    assert int(out_row[0]) == before_max + 1
    assert int(in_row[0]) == int(out_row[0]) + 1
    assert out_row[1] == when and in_row[1] == when
    assert out_row[2] == src and in_row[2] == dst
    assert out_row[3] == "TRANSFER" and in_row[3] == "TRANSFER"
    assert Decimal(out_row[4]) == -Decimal(amount_text)
    assert Decimal(in_row[4]) == Decimal(amount_text)
    assert out_row[5].endswith(dst)
    assert in_row[5].endswith(src)
    stored_out = db.transactions.get(txn_id=int(out_row[0]))
    stored_in = db.transactions.get(txn_id=int(in_row[0]))
    assert stored_out is not None and stored_in is not None
    assert stored_out.amount == -25000
    assert stored_in.amount == 25000
    assert stored_out.category == "TRANSFER" and stored_in.category == "TRANSFER"
=== END AC transfer-valid ===

=== AC transfer-conserves-cash ===
Intent: A valid transfer changes the two balances by opposite amounts and leaves their combined total unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "TRFSRC2"
dst = "TRFDST2"
with db_session() as db:
    db.accounts.create(account=src, name="Transfer Source")
    db.accounts.create(account=dst, name="Transfer Destination")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    if db.categories.get(category="TRFOPEN") is None:
        db.categories.create(category="TRFOPEN", description="Transfer opening")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=base, date="2026-04-01", account=src, category="TRFOPEN", amount=50000, memo="fund"
    )
    db.transactions.create(
        txn_id=base + 1, date="2026-04-01", account=dst, category="TRFOPEN", amount=1000, memo="fund"
    )

    def balance(code):
        return sum(r.amount for r in db.transactions.list(account=code))

    src_before, dst_before = balance(src), balance(dst)
    code, out, err = cli_runner("transfer", src, dst, "100.00", "2026-04-03")
    print(out)
    print(err)
    assert code == 0
    assert balance(src) == src_before - 10000
    assert balance(dst) == dst_before + 10000
    assert balance(src) + balance(dst) == src_before + dst_before
=== END AC transfer-conserves-cash ===

=== AC transfer-rejects-invalid ===
Intent: Equal accounts, a zero or negative amount, an unknown account, or an impossible date exit 3 and store no rows.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "TRFSRC3"
dst = "TRFDST3"
with db_session() as db:
    db.accounts.create(account=src, name="Transfer Source")
    db.accounts.create(account=dst, name="Transfer Destination")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    if db.categories.get(category="TRFOPEN") is None:
        db.categories.create(category="TRFOPEN", description="Transfer opening")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=base, date="2026-04-01", account=src, category="TRFOPEN", amount=50000, memo="fund"
    )
    before = len(db.transactions.list())
    cases = [
        (src, src, "10.00", "2026-04-03"),
        (src, dst, "0", "2026-04-03"),
        (src, dst, "0.00", "2026-04-03"),
        (src, dst, "-5.00", "2026-04-03"),
        (src, "TRFNONE", "10.00", "2026-04-03"),
        ("TRFNONE", dst, "10.00", "2026-04-03"),
        (src, dst, "1.234", "2026-04-03"),
        (src, dst, "10.00", "2026-02-30"),
    ]
    for args in cases:
        code, out, err = cli_runner("transfer", *args)
        print(args, code, err)
        assert code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC transfer-rejects-invalid ===

=== AC transfer-insufficient-funds ===
Intent: A transfer larger than the source balance exits 3 and stores neither row.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "TRFSRC4"
dst = "TRFDST4"
with db_session() as db:
    db.accounts.create(account=src, name="Transfer Source")
    db.accounts.create(account=dst, name="Transfer Destination")
    if db.categories.get(category="TRANSFER") is None:
        db.categories.create(category="TRANSFER", description="Internal transfer")
    if db.categories.get(category="TRFOPEN") is None:
        db.categories.create(category="TRFOPEN", description="Transfer opening")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=base, date="2026-04-01", account=src, category="TRFOPEN", amount=10000, memo="fund"
    )
    before_all = len(db.transactions.list())
    before_src = len(db.transactions.list(account=src))
    before_dst = len(db.transactions.list(account=dst))
    code, out, err = cli_runner("transfer", src, dst, "100.01", "2026-04-03")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before_all
    assert len(db.transactions.list(account=src)) == before_src
    assert len(db.transactions.list(account=dst)) == before_dst
=== END AC transfer-insufficient-funds ===

=== AC transfer-usage ===
Intent: A wrong argument count exits 2 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.transactions.list())
    code, out, err = cli_runner("transfer", "A", "B", "1.00")
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("transfer", "A", "B", "1.00", "2026-04-03", "extra")
    assert code == 2
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC transfer-usage ===

## User Acceptance

- None.

## Guardrails

- Both rows are stored or neither; every check completes before the first write.
- The two accounts differ and the amount is positive; zero and negative amounts are rejected.
- Both rows carry category `TRANSFER`, and their amounts are equal and opposite integer cents.
- Floating point is never used for money; diagnostics go to standard error only.
