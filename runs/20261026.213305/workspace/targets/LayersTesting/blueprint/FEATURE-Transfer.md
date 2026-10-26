# FEATURE: Transfer

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The `ledger transfer` command that records a paired debit and credit in category TRANSFER atomically. |
| Depends On | FEATURE-TxnPost.md, FEATURE-BalanceRules.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger transfer |
| Consumes | ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected |

## Purpose

`ledger transfer <from> <to> <amount> <date>` moves cash between two distinct accounts. It writes two transactions in category `TRANSFER` and prints both rows. Either both rows are stored or neither is.

## Behavior

- Exactly four arguments; the wrong count is a usage error handled by the CLI usage contract.
- Validate before the first write: the amount through `validation.parse_amount` (integer cents) and the date through `validation.parse_date`. The amount must be positive. `<from>` and `<to>` must differ. Both accounts must exist. The category `TRANSFER` must exist. Every violation raises `Rejected` (exit 3).
- Read the largest stored `txn_id` (last row of `transactions.list`, or none). The outgoing row takes that id plus one, and the incoming row the next id.
- Outgoing row: account `<from>`, amount `-amount`, category `TRANSFER`, memo is the words `transfer to` followed by a space and `<to>`.
- Incoming row: account `<to>`, amount `+amount`, category `TRANSFER`, memo is the words `transfer from` followed by a space and `<from>`.
- Call `balance_rules.check_final_balances` with both pending inserts so the source account is never left below zero. Rejection exits 3 and writes nothing.
- The id read, the balance check and both inserts run in one database transaction, so a concurrent command cannot take a balance below zero between check and write or reuse an id.
- Output: `txn_id,date,account,category,amount,memo` header, then the outgoing row and the incoming row, with amounts written by `csv_output`.
- Total cash held is unchanged by a transfer.

## Database Interface

- `FEATURE-TXN-001` — write: insert the outgoing and incoming rows - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-003` — read: list transactions to find the largest id and an account balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNT-002` — read: confirm an account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORY-002` — read: confirm category TRANSFER exists - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC transfer-success ===
Intent: A valid transfer stores consecutive TRANSFER rows, reads back, and conserves total cash.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

src, dst = "DRAWER1", "SAFE"
deposit = "100.00"
amount = "40.25"
day = "2026-04-03"

for args in (
    ("init",),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("txn", "post", src, "OPENING", deposit, day, "float"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

def total(db):
    return sum(r.amount for r in db.transactions.list())

with db_session() as db:
    ids_before = [r.txn_id for r in db.transactions.list()]
    cash_before = total(db)

code, out, err = cli_runner("transfer", src, dst, amount, day)
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
assert len(rows) == 3
first, second = rows[1], rows[2]
base = max(ids_before)
assert int(first[0]) == base + 1
assert int(second[0]) == base + 2
assert first[2] == src and second[2] == dst
assert first[1] == day and second[1] == day
assert first[3] == "TRANSFER" and second[3] == "TRANSFER"
assert Decimal(first[4]) == -Decimal(amount)
assert Decimal(second[4]) == Decimal(amount)
assert first[5].split() == ["transfer", "to", dst]
assert second[5].split() == ["transfer", "from", src]

with db_session() as db:
    out_row = db.transactions.get(txn_id=base + 1)
    in_row = db.transactions.get(txn_id=base + 2)
    assert out_row is not None and in_row is not None
    assert out_row.amount == -in_row.amount
    assert isinstance(out_row.amount, int)
    assert out_row.account == src and in_row.account == dst
    assert total(db) == cash_before
    src_balance = sum(r.amount for r in db.transactions.list(account=src))
    dst_balance = sum(r.amount for r in db.transactions.list(account=dst))
    assert Decimal(src_balance) / 100 == Decimal(deposit) - Decimal(amount)
    assert Decimal(dst_balance) / 100 == Decimal(amount)
=== END AC transfer-success ===

=== AC transfer-insufficient-funds ===
Intent: A transfer that would take the source below zero exits 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

src, dst = "PETTY", "SAFE"
day = "2026-04-04"

for args in (
    ("init",),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("txn", "post", src, "OPENING", "10.00", day, "float"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

with db_session() as db:
    before = [(r.txn_id, r.amount) for r in db.transactions.list()]

code, out, err = cli_runner("transfer", src, dst, "10.01", day)
print(out, err)
assert code == 3
assert out == ""

with db_session() as db:
    after = [(r.txn_id, r.amount) for r in db.transactions.list()]
assert after == before
=== END AC transfer-insufficient-funds ===

=== AC transfer-rejections ===
Intent: Same account, non-positive amounts, malformed amounts, bad dates and unknown accounts exit 3 and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

src, dst = "DRAWER1", "SAFE"
day = "2026-04-05"

for args in (
    ("init",),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("txn", "post", src, "OPENING", "500.00", day, "float"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

with db_session() as db:
    before = [(r.txn_id, r.amount) for r in db.transactions.list()]

cases = [
    (src, src, "5.00", day),
    (src, dst, "0", day),
    (src, dst, "0.00", day),
    (src, dst, "-5.00", day),
    (src, dst, "1.234", day),
    (src, dst, "abc", day),
    (src, dst, "5.00", "2026-02-30"),
    (src, "NOSUCH", "5.00", day),
    ("NOSUCH", dst, "5.00", day),
]
for case in cases:
    code, out, err = cli_runner("transfer", *case)
    print(case, code, out, err)
    assert code == 3
    assert out == ""

with db_session() as db:
    after = [(r.txn_id, r.amount) for r in db.transactions.list()]
assert after == before
=== END AC transfer-rejections ===

=== AC transfer-missing-category ===
Intent: A transfer when category TRANSFER is absent is rejected with exit 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

src, dst = "DRAWER1", "SAFE"
day = "2026-04-06"

code, out, err = cli_runner("init")
assert code == 0
code, out, err = cli_runner("load", "accounts", "sources/seed_accounts.csv")
print(out, err)
assert code == 0
with db_session() as db:
    db.categories.create(category="OPENING", description="Opening balance")
code, out, err = cli_runner("txn", "post", src, "OPENING", "50.00", day, "float")
print(out, err)
assert code == 0

with db_session() as db:
    before = [r.txn_id for r in db.transactions.list()]

code, out, err = cli_runner("transfer", src, dst, "5.00", day)
print(out, err)
assert code == 3
assert out == ""

with db_session() as db:
    after = [r.txn_id for r in db.transactions.list()]
assert after == before
=== END AC transfer-missing-category ===

## User Acceptance

- None.

## Guardrails

- Both transfer rows are stored or neither is; a rejected transfer changes nothing.
- No balance is ever left below zero.
- Amounts are integer cents at every layer; no floating point.
- The application never reads `sources/run.sh` or any seed file.
