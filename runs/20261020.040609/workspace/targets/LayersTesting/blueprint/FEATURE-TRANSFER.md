# FEATURE: Transfer Between Accounts

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Moves an amount between two accounts as two linked rows in category TRANSFER. |
| Depends On  | FEATURE-TXN-POST.md, FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-AMOUNT.md, FEATURE-VALIDATE-DATE.md |
| Provides    | ledger transfer |

## Purpose

`ledger transfer <from> <to> <amount> <date>` records an internal movement of cash. It stores two rows in category `TRANSFER`: a negative row on `<from>` and a positive row on `<to>`, with the memos and ids the Commands table specifies.

## Behavior

1. Validate `<from>`, `<to>`, `<amount>`, and `<date>` with the shared validators.
2. Open one database transaction.
3. Assign the outgoing row the next `txn_id` (one more than the largest present, or `1` in an empty table) and the incoming row the id after it.
4. Insert both rows, check that no account balance is below zero, then commit.
5. Write the header row and the two transaction rows to standard output, outgoing row first.

Identical accounts, non-positive amounts, and unknown accounts are rejected before any row is written. Those cases are specified in FEATURE-TRANSFER-REJECTION.md.

## Programmatic Acceptance

=== AC transfer-stores-two-linked-rows ===
Intent: A successful transfer stores a negative row on the source and a positive row on the destination, with consecutive ids and the TRANSFER category.

import csv
import io
import os
import tempfile
from decimal import Decimal

from cli.testing import cli_runner
from persistence import open_database

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0, err

db = open_database(os.environ["DATABASE_URL"])
previous_max = max(row.txn_id for row in db.transactions.list())

from_account = "DRAWER1"
to_account = "SAFE"
amount_text = "500.00"
amount_cents = 50000
date = "2026-04-03"

code, out, err = cli_runner("transfer", from_account, to_account, amount_text, date)
assert code == 0, err
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 3, rows
header, outgoing_fields, incoming_fields = rows
assert header == ["txn_id", "date", "account", "category", "amount", "memo"]

outgoing = dict(zip(header, outgoing_fields))
incoming = dict(zip(header, incoming_fields))
assert int(outgoing["txn_id"]) == previous_max + 1
assert int(incoming["txn_id"]) == previous_max + 2
assert outgoing["account"] == from_account
assert incoming["account"] == to_account
assert outgoing["category"] == incoming["category"] == "TRANSFER"
assert outgoing["date"] == incoming["date"] == date
assert int(Decimal(outgoing["amount"]).scaleb(2)) == -amount_cents
assert int(Decimal(incoming["amount"]).scaleb(2)) == amount_cents
assert outgoing["memo"].split() == ["transfer", "to", to_account]
assert incoming["memo"].split() == ["transfer", "from", from_account]

for fields in (outgoing, incoming):
    code, out, err = cli_runner("txn", "get", fields["txn_id"])
    assert code == 0, err
    stored = list(csv.reader(io.StringIO(out)))
    assert stored[1] == [fields[name] for name in header]
=== END AC transfer-stores-two-linked-rows ===

=== AC transfer-rejects-overdraft-and-changes-nothing ===
Intent: A transfer that would leave the source account below zero exits 3 and stores no rows.

import os
import tempfile

from cli.testing import cli_runner
from persistence import open_database

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")
for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0, err

db = open_database(os.environ["DATABASE_URL"])


def snapshot():
    return sorted((row.txn_id, row.account, row.amount) for row in db.transactions.list())


before = snapshot()
code, out, err = cli_runner("transfer", "PETTY", "SAFE", "99999999.99", "2026-04-03")
assert code == 3, err
assert out == ""
assert snapshot() == before
=== END AC transfer-rejects-overdraft-and-changes-nothing ===

## User Acceptance

- None.

## Guardrails

- Both rows of a transfer are stored in one database transaction; a transfer never stores one row alone.
- The transfer reuses the posting path's id assignment and does not compute ids separately.
- No account balance may be left below zero by a transfer.
