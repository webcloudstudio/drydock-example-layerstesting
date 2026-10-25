# FEATURE: Transaction Post

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger txn post`, recording one receipt or payment against an account in integer cents. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-LoadCategories.md, FEATURE-LedgerCore.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn post |
| Consumes | transactions.create, transactions.list, accounts.list, categories.get |

## Purpose

Post a single transaction. Every input and the non-negative balance rule are checked before the first
write, so a rejected post changes nothing.

## Command Contract

| Aspect | Rule |
|--------|------|
| Invocation | `ledger txn post <account> <category> <amount> <date> [<memo>]`: four or five arguments. |
| Amount | Matches `-?DIGITS[.D[D]]`, at most two decimals, never zero. Parsed to integer cents by the shared core; no floating point. |
| Date | A real calendar date written `YYYY-MM-DD`. |
| Memo | Optional, 0 to 60 characters, no comma or newline. Absent means the empty string. |
| Account and category | Both must exist; otherwise exit 3. |
| Transaction id | One more than the largest `txn_id` present, or `1` in an empty table. |
| Balance | If the account balance after the post would be below zero, exit 3 before any write. |
| Success stdout | Header `txn_id,date,account,category,amount,memo`, then the new row with the amount as two-decimal text. |
| Rejection | Exit 3, nothing on stdout, no row stored. |
| Wrong argument count | Exit 2, nothing on stdout. |

## Database Interface

- `FEATURE-TXN-003` — write: create a transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-002` — read: list transactions to find the largest id and the account balance - supplies: `account` - returns: `txn_id`, `amount`
- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`
- `FEATURE-CATEGORY-001` — read: confirm the category exists - supplies: `category` - returns: `category`

## Programmatic Acceptance

=== AC txn-post-success ===
Intent: Posting a transaction prints its row with the next id and stores integer cents that read back.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSS1"
    cat = "TPOSSC1"
    db.accounts.create(account=acct, name="Post Success")
    db.categories.create(category=cat, description="Post Success Cat")
    next_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    amount_text = "45.50"
    day = "2026-04-01"
    memo = "walk in sale"
    rc, out, err = cli_runner("txn", "post", acct, cat, amount_text, day, memo)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 2
    assert int(rows[1][0]) == next_id
    assert rows[1][1] == day
    assert rows[1][2] == acct
    assert rows[1][3] == cat
    assert rows[1][4] == amount_text
    assert rows[1][5] == memo
    got = db.transactions.get(txn_id=next_id)
    assert got is not None
    assert got.date == day
    assert got.account == acct
    assert got.category == cat
    assert got.amount == int(amount_text.replace(".", ""))
    assert got.memo == memo
=== END AC txn-post-success ===

=== AC txn-post-id-increments ===
Intent: Two successive posts receive consecutive transaction ids.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSI1"
    cat = "TPOSIC1"
    db.accounts.create(account=acct, name="Post Ids")
    db.categories.create(category=cat, description="Post Ids Cat")
    first_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    rc1, out1, err1 = cli_runner("txn", "post", acct, cat, "10.00", "2026-04-01", "one")
    rc2, out2, err2 = cli_runner("txn", "post", acct, cat, "20.00", "2026-04-01", "two")
    print(err1)
    print(err2)
    assert rc1 == 0
    assert rc2 == 0
    row1 = list(csv.reader(io.StringIO(out1)))[1]
    row2 = list(csv.reader(io.StringIO(out2)))[1]
    assert int(row1[0]) == first_id
    assert int(row2[0]) == first_id + 1
=== END AC txn-post-id-increments ===

=== AC txn-post-no-memo ===
Intent: A post without a memo stores and prints an empty memo.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSN1"
    cat = "TPOSNC1"
    db.accounts.create(account=acct, name="Post No Memo")
    db.categories.create(category=cat, description="Post No Memo Cat")
    next_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    rc, out, err = cli_runner("txn", "post", acct, cat, "3.00", "2026-04-02")
    print(err)
    assert rc == 0
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[5] == ""
    got = db.transactions.get(txn_id=next_id)
    assert got is not None
    assert got.memo == ""
=== END AC txn-post-no-memo ===

=== AC txn-post-negative-with-funds ===
Intent: A negative post is accepted when the account balance stays at or above zero and is stored as negative cents.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSG1"
    cat = "TPOSGC1"
    db.accounts.create(account=acct, name="Post Negative")
    db.categories.create(category=cat, description="Post Negative Cat")
    funding = 5000
    seed_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=seed_id, date="2026-04-01", account=acct,
        category=cat, amount=funding, memo="",
    )
    amount_text = "-12.34"
    rc, out, err = cli_runner("txn", "post", acct, cat, amount_text, "2026-04-02", "tape")
    print(err)
    assert rc == 0
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[4] == amount_text
    got = db.transactions.get(txn_id=int(row[0]))
    assert got is not None
    assert got.amount == int(amount_text.replace(".", ""))
=== END AC txn-post-negative-with-funds ===

=== AC txn-post-reject-overdraw ===
Intent: A post that would leave the account balance below zero exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSO1"
    cat = "TPOSOC1"
    db.accounts.create(account=acct, name="Post Overdraw")
    db.categories.create(category=cat, description="Post Overdraw Cat")
    seed_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=seed_id, date="2026-04-01", account=acct,
        category=cat, amount=1000, memo="",
    )
    before = len(db.transactions.list())
    rc, out, err = cli_runner("txn", "post", acct, cat, "-10.01", "2026-04-02")
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reject-overdraw ===

=== AC txn-post-reject-unknown-account ===
Intent: A post to an unknown account exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    cat = "TPOSU1C"
    absent = "TPOSU1"
    db.categories.create(category=cat, description="Unknown Account Cat")
    assert db.accounts.get(account=absent) is None
    before = len(db.transactions.list())
    rc, out, err = cli_runner("txn", "post", absent, cat, "1.00", "2026-04-01")
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reject-unknown-account ===

=== AC txn-post-reject-unknown-category ===
Intent: A post to an unknown category exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSK1"
    absent = "TPOSKC1"
    db.accounts.create(account=acct, name="Unknown Category")
    assert db.categories.get(category=absent) is None
    before = len(db.transactions.list())
    rc, out, err = cli_runner("txn", "post", acct, absent, "1.00", "2026-04-01")
    print(err)
    assert rc == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reject-unknown-category ===

=== AC txn-post-reject-zero-amount ===
Intent: A zero amount in any spelling exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSZ1"
    cat = "TPOSZC1"
    db.accounts.create(account=acct, name="Post Zero")
    db.categories.create(category=cat, description="Post Zero Cat")
    before = len(db.transactions.list())
    for zero in ("0", "0.0", "0.00", "-0.00"):
        rc, out, err = cli_runner("txn", "post", acct, cat, zero, "2026-04-01")
        print(err)
        assert rc == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reject-zero-amount ===

=== AC txn-post-reject-bad-memo ===
Intent: A memo longer than 60 characters or containing a comma exits 3 and stores nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "TPOSM1"
    cat = "TPOSMC1"
    db.accounts.create(account=acct, name="Post Memo")
    db.categories.create(category=cat, description="Post Memo Cat")
    before = len(db.transactions.list())
    too_long = "m" * 61
    for bad in (too_long, "has,comma"):
        rc, out, err = cli_runner("txn", "post", acct, cat, "1.00", "2026-04-01", bad)
        print(err)
        assert rc == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-reject-bad-memo ===

=== AC txn-post-usage ===
Intent: A post with too few or too many arguments exits 2 and writes nothing to stdout.

from cli.testing import cli_runner

too_few = ("txn", "post", "A", "B", "1.00")
too_many = ("txn", "post", "A", "B", "1.00", "2026-04-01", "memo", "extra")
for args in (("txn", "post"), too_few, too_many):
    rc, out, err = cli_runner(*args)
    assert rc == 2
    assert out == ""
=== END AC txn-post-usage ===

## User Acceptance

- None.

## Guardrails

- Amounts are parsed to integer cents by the shared core; no floating point at any layer.
- Every input and the balance rule are checked before the first write; a rejected post stores nothing.
- Nothing is written to stdout on failure.
- The transaction id is never supplied by the caller; it is one more than the largest present, or 1.
