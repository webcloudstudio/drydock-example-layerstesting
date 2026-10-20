# FEATURE: Transaction Post

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Post a new cash transaction through `ledger txn post`, assigning the next transaction id. |
| Depends On  | DATABASE.md, FEATURE-ACCOUNT-ADD.md, FEATURE-LOAD-CATEGORIES.md, FEATURE-NONNEGATIVE-BALANCE.md, FEATURE-VALIDATE-CODE.md, FEATURE-VALIDATE-TEXT.md, FEATURE-VALIDATE-AMOUNT.md, FEATURE-VALIDATE-DATE.md |
| Provides    | ledger txn post |
| Consumes    | accounts.get, categories.get, transactions.list, transactions.create |

## Purpose

`ledger txn post <account> <category> <amount> <date> [<memo>]` records one receipt or payment
against an existing account and category. The command assigns the transaction id; the caller
never supplies it.

## Behavior

- Validate the account and category codes, the amount, the date, and the memo. The memo is optional
  and holds 0 to 60 characters with no comma or newline. Any violation exits 3.
- Read the account and the category. An unknown account or category exits 3.
- Read the largest existing `txn_id`. The new id is one more than that, or `1` when the table is
  empty.
- Insert the row, check that no account balance is below zero, then commit.
- On success, write the header `txn_id,date,account,category,amount,memo` and the new row. Amounts
  are written with exactly two decimal places.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-post-round-trip ===
Intent: Posting a transaction exits 0, writes the header and the new row, and persists the row with integer cents.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
amount_text = "45.50"
amount_cents = 4550
date_value = "2026-04-01"
memo_value = "walk in sale"

exit_code, out, err = cli_runner(
    "txn", "post", account_code, category_code, amount_text, date_value, memo_value
)
print(out)
print(err)
assert exit_code == 0
lines = out.splitlines()
assert lines[0] == "txn_id,date,account,category,amount,memo"
new_id = int(lines[1].split(",")[0])
with db_session(dsn) as db:
    row = db.transactions.get(txn_id=new_id)
    assert row.txn_id == new_id
    assert row.account == account_code
    assert row.category == category_code
    assert row.amount == amount_cents
    assert row.memo == memo_value
=== END AC txn-post-round-trip ===

=== AC txn-post-first-id-is-one ===
Intent: Posting into an empty transactions table assigns txn_id 1.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
first_id = 1

exit_code, out, err = cli_runner("txn", "post", account_code, category_code, "10.00", "2026-04-01")
print(out)
print(err)
assert exit_code == 0
assert int(out.splitlines()[1].split(",")[0]) == first_id
=== END AC txn-post-first-id-is-one ===

=== AC txn-post-id-follows-largest ===
Intent: The posted txn_id is one more than the largest txn_id present, even when ids have gaps.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
seeded_id = 7
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    db.transactions.create(
        txn_id=seeded_id, date=date_value, account=account_code, category=category_code,
        amount=100, memo="seed",
    )

exit_code, out, err = cli_runner("txn", "post", account_code, category_code, "1.00", date_value)
print(out)
print(err)
assert exit_code == 0
assert int(out.splitlines()[1].split(",")[0]) == seeded_id + 1
=== END AC txn-post-id-follows-largest ===

=== AC txn-post-rejects-unknown-references ===
Intent: An unknown account or an unknown category exits 3 and leaves the transaction count unchanged.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
unknown_account = "NOSUCH"
unknown_category = "NOCAT"
date_value = "2026-04-01"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    count_before = len(db.transactions.list())

exit_code_account, out_account, err_account = cli_runner(
    "txn", "post", unknown_account, category_code, "1.00", date_value
)
exit_code_category, out_category, err_category = cli_runner(
    "txn", "post", account_code, unknown_category, "1.00", date_value
)
print(err_account)
print(err_category)
assert exit_code_account == 3
assert exit_code_category == 3
assert out_account == ""
assert out_category == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-post-rejects-unknown-references ===

=== AC txn-post-rejects-invalid-amount ===
Intent: Zero, a value with three decimal places, and a value that would drive the balance below zero each exit 3 and insert nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
date_value = "2026-04-01"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    count_before = len(db.transactions.list())
zero_amount = "0"
three_places = "1.234"
overdraw_amount = "-1.00"

exit_zero, out_zero, err_zero = cli_runner("txn", "post", account_code, category_code, zero_amount, date_value)
exit_places, out_places, err_places = cli_runner("txn", "post", account_code, category_code, three_places, date_value)
exit_overdraw, out_overdraw, err_overdraw = cli_runner("txn", "post", account_code, category_code, overdraw_amount, date_value)
print(err_zero)
print(err_places)
print(err_overdraw)
assert exit_zero == 3
assert exit_places == 3
assert exit_overdraw == 3
assert out_zero == ""
assert out_places == ""
assert out_overdraw == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-post-rejects-invalid-amount ===

=== AC txn-post-rejects-invalid-date ===
Intent: A date that is not a real calendar date exits 3 and inserts nothing.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

dsn = os.path.join(tempfile.mkdtemp(), "ledger.db")
os.environ["DATABASE_URL"] = dsn
account_code = "CASH1"
category_code = "SALES"
with db_session(dsn) as db:
    db.accounts.create(account=account_code, name="Cash One")
    db.categories.create(category=category_code, description="Sales receipts")
    count_before = len(db.transactions.list())
bad_date = "2026-02-30"

exit_code, out, err = cli_runner("txn", "post", account_code, category_code, "1.00", bad_date)
print(err)
assert exit_code == 3
assert out == ""
with db_session(dsn) as db:
    assert len(db.transactions.list()) == count_before
=== END AC txn-post-rejects-invalid-date ===

## User Acceptance

- None.

## Guardrails

- A caller never supplies a `txn_id` to `txn post`; the command assigns it.
- A posted amount of zero is never stored.
- A post that leaves any account balance below zero is never committed.
