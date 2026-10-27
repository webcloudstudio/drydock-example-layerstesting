# FEATURE: Transaction Post

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn post`, which validates a new cash transaction in full and stores it with the next transaction id. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-AccountGet.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger txn post |
| Consumes | ledger, accounts, categories, transactions |

## Purpose

Record one receipt (positive) or payment (negative) against an account and category, assigning its id automatically.

## Trigger

`ledger txn post <account> <category> <amount> <date> [<memo>]` invoked from the command line.

## Sequence

1. Require four or five arguments after `post`; otherwise raise the shared usage error (exit 2).
2. Validate the amount with the shared parser: `-?DIGITS[.D[D]]`, at most two decimals, never zero; convert to integer cents with no floating point.
3. Validate the date as a real Gregorian calendar date `YYYY-MM-DD` (February 29 only in leap years).
4. Validate the memo (0 to 60 characters, no comma, no newline); an omitted memo is stored as the empty string.
5. Confirm the account and the category exist; either missing exits 3.
6. Compute the account's balance from its stored transactions and confirm balance plus amount is not below zero.
7. Assign `txn_id` as one more than the largest stored id, or 1 when no transaction exists.
8. Only after every check passes, create the row and write the header `txn_id,date,account,category,amount,memo` and the new row with the amount at exactly two decimals.

Any failure in steps 2 to 6 exits 3 and writes nothing.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`
- `FEATURE-CATEGORY-002` — read: confirm the category exists - supplies: `category` - returns: `category`
- `FEATURE-TXN-005` — read: list transactions to compute the balance and the largest id - supplies: `account` - returns: `txn_id`, `amount`
- `FEATURE-TXN-001` — write: create the transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Behavior Rules

- Amounts are integer cents at every layer.
- A rejected post changes no stored record.
- Output uses `\n` line endings and no quoting.

## Programmatic Acceptance

=== AC txn-post-success ===
Intent: Posting a valid transaction exits 0, writes the new row with the next id, and a separate read returns every stored column.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP1"
cat = "ZTP1"
amount_text = "45.50"
cents = 4550
date = "2026-04-01"
memo = "walk in sale"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    before = [r.txn_id for r in db.transactions.list()]
    expected_id = (max(before) + 1) if before else 1
    exit_code, out, err = cli_runner("txn", "post", acct, cat, amount_text, date, memo)
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(expected_id), date, acct, cat, amount_text, memo]
    back = db.transactions.get(txn_id=expected_id)
    assert back is not None
    assert back.date == date
    assert back.account == acct
    assert back.category == cat
    assert back.amount == cents
    assert back.memo == memo
=== END AC txn-post-success ===

=== AC txn-post-first-id ===
Intent: In an empty transaction table the first posted transaction receives id 1.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP2"
cat = "ZTP2"
amount_text = "10.00"
with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    assert db.transactions.list() == []
    db.accounts.create(account=acct, name="First Id")
    db.categories.create(category=cat, description="First Id")
    exit_code, out, err = cli_runner("txn", "post", acct, cat, amount_text, "2026-04-02")
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][0] == str(1)
    assert db.transactions.get(txn_id=1) is not None
=== END AC txn-post-first-id ===

=== AC txn-post-no-memo ===
Intent: A transaction posted without a memo writes an empty final memo field and stores an empty memo.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP3"
cat = "ZTP3"
with db_session() as db:
    db.accounts.create(account=acct, name="No Memo")
    db.categories.create(category=cat, description="No Memo")
    before = [r.txn_id for r in db.transactions.list()]
    expected_id = (max(before) + 1) if before else 1
    exit_code, out, err = cli_runner("txn", "post", acct, cat, "5.00", "2026-04-03")
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows[1]) == 6
    assert rows[1][5] == ""
    back = db.transactions.get(txn_id=expected_id)
    assert back is not None
    assert back.memo == ""
=== END AC txn-post-no-memo ===

=== AC txn-post-negative-covered ===
Intent: A negative amount is accepted when the account balance stays non-negative, and the output carries a leading minus with two decimals.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP4"
cat = "ZTP4"
txn_id = 930001
funded_cents = 5000
spend_text = "-12.34"
with db_session() as db:
    db.accounts.create(account=acct, name="Spender")
    db.categories.create(category=cat, description="Spend")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=funded_cents, memo=""
    )
    exit_code, out, err = cli_runner("txn", "post", acct, cat, spend_text, "2026-04-02", "tape")
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][4] == spend_text
    assert Decimal(rows[1][4]) == Decimal(spend_text)
=== END AC txn-post-negative-covered ===

=== AC txn-post-negative-balance-rejected ===
Intent: A post that would leave the account balance below zero exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP5"
cat = "ZTP5"
with db_session() as db:
    db.accounts.create(account=acct, name="Broke")
    db.categories.create(category=cat, description="Spend")
    before = len(db.transactions.list())
    exit_code, out, err = cli_runner("txn", "post", acct, cat, "-1000.00", "2026-04-04")
    print(exit_code, out, err)
    assert exit_code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-negative-balance-rejected ===

=== AC txn-post-reference-rejected ===
Intent: An unknown category or an unknown account is rejected with exit 3 and nothing is stored.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP6"
cat = "ZTP6"
missing = "ZTPNONE"
with db_session() as db:
    db.accounts.create(account=acct, name="Refs")
    db.categories.create(category=cat, description="Refs")
    before = len(db.transactions.list())
    for args in ((acct, missing), (missing, cat)):
        exit_code, out, err = cli_runner("txn", "post", args[0], args[1], "1.00", "2026-04-01")
        print(exit_code, out, err)
        assert exit_code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reference-rejected ===

=== AC txn-post-amount-rejected ===
Intent: Amounts with more than two decimals, zero amounts, and non-numeric amounts are rejected with exit 3 and store nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP7"
cat = "ZTP7"
bad_amounts = ["1.234", "0", "0.00", "abc", "1,5"]
with db_session() as db:
    db.accounts.create(account=acct, name="Amounts")
    db.categories.create(category=cat, description="Amounts")
    before = len(db.transactions.list())
    for bad in bad_amounts:
        exit_code, out, err = cli_runner("txn", "post", acct, cat, bad, "2026-04-01")
        print(bad, exit_code, out, err)
        assert exit_code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-amount-rejected ===

=== AC txn-post-date-rules ===
Intent: Impossible dates and February 29 in non-leap Gregorian years are rejected with exit 3, while February 29 in a leap year is accepted.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP8"
cat = "ZTP8"
rejected = ["2026-02-30", "2026-02-29", "2100-02-29", "2026-13-01", "2026-4-1"]
accepted = ["2024-02-29", "2000-02-29"]
with db_session() as db:
    db.accounts.create(account=acct, name="Dates")
    db.categories.create(category=cat, description="Dates")
    before = len(db.transactions.list())
    for bad in rejected:
        exit_code, out, err = cli_runner("txn", "post", acct, cat, "1.00", bad)
        print(bad, exit_code, out, err)
        assert exit_code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
    for good in accepted:
        exit_code, out, err = cli_runner("txn", "post", acct, cat, "1.00", good)
        print(good, exit_code, out, err)
        assert exit_code == 0
    assert len(db.transactions.list()) == before + len(accepted)
=== END AC txn-post-date-rules ===

=== AC txn-post-memo-rejected ===
Intent: A memo longer than 60 characters or containing a comma is rejected with exit 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTP9"
cat = "ZTP9"
too_long = "m" * 61
with_comma = "left,right"
with db_session() as db:
    db.accounts.create(account=acct, name="Memos")
    db.categories.create(category=cat, description="Memos")
    before = len(db.transactions.list())
    for bad in (too_long, with_comma):
        exit_code, out, err = cli_runner("txn", "post", acct, cat, "1.00", "2026-04-01", bad)
        print(exit_code, out, err)
        assert exit_code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-memo-rejected ===

## User Acceptance

- None.

## Guardrails

- Every input and rule is checked before the first write; a rejected post changes nothing.
- No floating point is used for money at any layer.
- Persistence is reached only through the generated persistence package.
