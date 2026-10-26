# FEATURE: Txn Post

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger txn post`, which validates and stores one transaction with an assigned id under the non-negative balance rule. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-LoadCategories.md, FEATURE-Validation.md, FEATURE-BalanceRules.md, FEATURE-CsvOutput.md, FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger txn post |
| Consumes | ledger.register_command, persistence.open_database, validation.parse_amount, validation.parse_date, validation.check_code, validation.check_text, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.Rejected |

## Purpose

Record one receipt or payment against an account and category. Source Rules 1 to 7 apply: every input is checked before the first write, the balance never goes below zero, amounts are integer cents, dates are real calendar dates.

## Behavior

- Invocation: `ledger txn post <account> <category> <amount> <date> [<memo>]`; four or five arguments.
- Validation, all before any write, each failure exiting 3: account and category codes (1 to 12 of `A-Z0-9`); amount matching `-?DIGITS[.D[D]]` (no leading dot, `+`, spaces or separators, at most two decimals, never zero in any form) converted to integer cents with integer arithmetic; date a real `YYYY-MM-DD` date (`2028-02-29` valid, `2026-02-29` and `2026-02-30` invalid); memo 0 to 60 characters with no comma or newline.
- The account must exist (`db.accounts.get`) and the category must exist (`db.categories.get`); otherwise exit 3.
- Balance: the resulting balance of the account (sum of its stored amounts plus the new amount) is checked with `balance_rules.check_final_balances`; a negative result exits 3.
- The new `txn_id` is the largest stored id plus one, or 1 for an empty table, computed from `db.transactions.list`. The id computation, the balance check and the insert run in one database transaction so two concurrent posts never share an id.
- A missing memo stores the empty string.
- Success writes the header `txn_id,date,account,category,amount,memo` and the new row, amount with exactly two decimals.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORY-002` — read: confirm the category exists - supplies: `category` - returns: `category`, `description`
- `FEATURE-TXN-003` — read: list stored transactions for id and balance computation - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-001` — write: create the transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-post-success ===
Intent: A valid post stores the row with the next id and prints it; the stored row reads back with integer cents.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST1"
cat = "ZQPOSTC1"
amount = "45.50"
date = "2026-04-01"
memo = "walk in sale"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    ids = [r.txn_id for r in db.transactions.list()]
    expected_id = max(ids) + 1 if ids else 1
    code, out, err = cli_runner("txn", "post", acct, cat, amount, date, memo)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 2
    assert rows[1] == [str(expected_id), date, acct, cat, amount, memo]
    back = db.transactions.get(txn_id=expected_id)
    assert back is not None
    assert back.amount == int(Decimal(amount) * 100)
    assert isinstance(back.amount, int)
    assert (back.date, back.account, back.category, back.memo) == (date, acct, cat, memo)
=== END AC txn-post-success ===

=== AC txn-post-no-memo ===
Intent: A post without a memo stores an empty memo and prints an empty final field.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST2"
cat = "ZQPOSTC2"
amount = "10.00"
date = "2026-04-02"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    code, out, err = cli_runner("txn", "post", acct, cat, amount, date)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows[1]) == 6
    assert rows[1][5] == ""
    back = db.transactions.get(txn_id=int(rows[1][0]))
    assert back.memo == ""
=== END AC txn-post-no-memo ===

=== AC txn-post-consecutive-ids ===
Intent: Two successive posts receive ids that differ by one.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST3"
cat = "ZQPOSTC3"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    got = []
    for amount in ("5.00", "6.00"):
        code, out, err = cli_runner("txn", "post", acct, cat, amount, "2026-04-03")
        print(out)
        print(err)
        assert code == 0
        got.append(int(list(csv.reader(io.StringIO(out)))[1][0]))
    assert got[1] == got[0] + 1
=== END AC txn-post-consecutive-ids ===

=== AC txn-post-unknown-references ===
Intent: An unknown account or unknown category exits 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST4"
cat = "ZQPOSTC4"
missing = "ZQNOSUCH4"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "post", missing, cat, "1.00", "2026-04-01")
    assert code == 3
    assert out == ""
    code, out, err = cli_runner("txn", "post", acct, missing, "1.00", "2026-04-01")
    assert code == 3
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-unknown-references ===

=== AC txn-post-bad-amounts ===
Intent: Malformed, over-precise and zero amounts are rejected with exit 3 and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST5"
cat = "ZQPOSTC5"
bad = ["1.234", ".50", "+5.00", "0", "0.00", "-0", "1,000.00", " 5.00", "abc", "5.", "--5"]
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    before = len(db.transactions.list())
    for amount in bad:
        code, out, err = cli_runner("txn", "post", acct, cat, amount, "2026-04-01")
        assert code == 3, amount
        assert out == "", amount
    assert len(db.transactions.list()) == before
=== END AC txn-post-bad-amounts ===

=== AC txn-post-dates ===
Intent: Leap days are valid only in leap years and impossible dates are rejected.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST6"
cat = "ZQPOSTC6"
good_leap = "2028-02-29"
bad_dates = ["2026-02-29", "2026-02-30", "2026-13-01", "2026-4-1", "not-a-date"]
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    for d in bad_dates:
        before = len(db.transactions.list())
        code, out, err = cli_runner("txn", "post", acct, cat, "1.00", d)
        assert code == 3, d
        assert out == "", d
        assert len(db.transactions.list()) == before, d
    code, out, err = cli_runner("txn", "post", acct, cat, "1.00", good_leap)
    print(out)
    print(err)
    assert code == 0
=== END AC txn-post-dates ===

=== AC txn-post-negative-balance ===
Intent: A payment larger than the balance is rejected with exit 3, while one within the balance is accepted.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST7"
cat = "ZQPOSTC7"
deposit = "100.00"
too_much = "-100.01"
fits = "-40.00"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    code, out, err = cli_runner("txn", "post", acct, cat, "-1.00", "2026-04-01")
    assert code == 3
    assert out == ""
    assert len(db.transactions.list(account=acct)) == 0
    code, out, err = cli_runner("txn", "post", acct, cat, deposit, "2026-04-01")
    assert code == 0
    code, out, err = cli_runner("txn", "post", acct, cat, too_much, "2026-04-02")
    assert code == 3
    assert out == ""
    assert len(db.transactions.list(account=acct)) == 1
    code, out, err = cli_runner("txn", "post", acct, cat, fits, "2026-04-02")
    print(out)
    print(err)
    assert code == 0
    balance = sum(r.amount for r in db.transactions.list(account=acct))
    assert balance == int(Decimal(deposit) * 100) + int(Decimal(fits) * 100)
=== END AC txn-post-negative-balance ===

=== AC txn-post-bad-text ===
Intent: Invalid codes and memos are rejected with exit 3 and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQPOST8"
cat = "ZQPOSTC8"
long_memo = "m" * 61
ok_memo = "m" * 60
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    db.categories.create(category=cat, description="Post Category")
    before = len(db.transactions.list())
    for args in (
        ("zqlower", cat, "1.00", "2026-04-01"),
        (acct, "bad code", "1.00", "2026-04-01"),
        (acct, cat, "1.00", "2026-04-01", long_memo),
        (acct, cat, "1.00", "2026-04-01", "has,comma"),
    ):
        code, out, err = cli_runner("txn", "post", *args)
        assert code == 3, args
        assert out == "", args
    assert len(db.transactions.list()) == before
    code, out, err = cli_runner("txn", "post", acct, cat, "1.00", "2026-04-01", ok_memo)
    print(err)
    assert code == 0
=== END AC txn-post-bad-text ===

## User Acceptance

- None.

## Guardrails

- No floating point is used for money at any layer; amounts are parsed and stored as integer cents.
- A rejected post writes nothing; every check runs before the insert.
- Do not read `sources/run.sh` or any seed file from application code.
- A failing command writes nothing to stdout and never echoes a DSN or credential.
