# FEATURE: Txn Post

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `ledger txn post` command validates and stores one new transaction and prints its row. |
| Depends On  | FEATURE-BalanceRules.md, FEATURE-CliFoundation.md, DATABASE.md |
| Provides    | ledger txn post |
| Consumes    | transactions.create, transactions.list, accounts.get, categories.get, check_balances |

## Purpose

`ledger txn post <account> <category> <amount> <date> [<memo>]` records one receipt or payment
against an account. The command checks every input and the resulting balance before its first
write, so a rejected post changes nothing.

## Trigger

An operator runs `./ledger txn post` with four or five arguments.

## Sequence

1. Reject a wrong argument count with exit 2 (fewer than four or more than five arguments after `post`).
2. Validate the account code, category code, amount, date, and memo with the shared validators. Any invalid value exits 3.
3. Look up the account with `accounts.get` and the category with `categories.get`. An unknown account or category exits 3.
4. Convert the amount to integer cents. Zero and amounts with more than two decimal places exit 3.
5. List the account's transactions with `transactions.list` and run `check_balances` with the proposed added row. A balance below zero exits 3.
6. List all transactions with `transactions.list`, take the largest `txn_id` plus one (or `1` when none exist) as the new id.
7. Store the row with `transactions.create`, then print the header row and the stored row as CSV. Exit 0.

## Output

```text
txn_id,date,account,category,amount,memo
<id>,<date>,<account>,<category>,<amount with two decimals>,<memo>
```

An omitted memo is stored and printed as an empty field. Failures write one diagnostic line to standard error and nothing to standard output.

## Reads

- `accounts.get`, `categories.get`, `transactions.list`

## Writes

- `transactions.create`, only after every check has passed

## Database Interface

- `FEATURE-TRANSACTIONS-001` — write: create the new transaction - supplies: `txn_id`, `date`, `account`, `category`, `amount`, `memo` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TRANSACTIONS-003` — read: list transactions to find the largest id and the account balance - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-ACCOUNTS-002` — read: confirm the account exists - supplies: `account` - returns: `account`, `name`
- `FEATURE-CATEGORIES-002` — read: confirm the category exists - supplies: `category` - returns: `category`, `description`

## Programmatic Acceptance

=== AC txn-post-roundtrip ===
Intent: A valid post prints the stored row, assigns the largest id plus one, and persists the amount as integer cents.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TPOST1"
cat = "TPCAT1"
amount_text = "45.50"
cents = 4550
when = "2026-04-01"
memo = "walk in sale"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Post Category")
    before_max = max([r.txn_id for r in db.transactions.list()] or [0])
    code, out, err = cli_runner("txn", "post", acct, cat, amount_text, when, memo)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert len(rows) == 2
    data = rows[1]
    assert int(data[0]) == before_max + 1
    assert data[1] == when
    assert data[2] == acct
    assert data[3] == cat
    assert data[4] == amount_text
    assert data[5] == memo
    stored = db.transactions.get(txn_id=int(data[0]))
    assert stored is not None
    assert stored.amount == cents
    assert isinstance(stored.amount, int)
    assert stored.account == acct
    assert stored.memo == memo
=== END AC txn-post-roundtrip ===

=== AC txn-post-memo-optional ===
Intent: A post without a memo succeeds and stores an empty memo.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TPOST2"
cat = "TPCAT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Post Category")
    code, out, err = cli_runner("txn", "post", acct, cat, "10.00", "2026-04-02")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    stored = db.transactions.get(txn_id=int(rows[1][0]))
    assert stored is not None
    assert stored.memo == ""
    assert len(rows[1]) == 6
=== END AC txn-post-memo-optional ===

=== AC txn-post-rejects-invalid ===
Intent: An unknown account, unknown category, over-precise amount, zero amount, or impossible date exits 3 and stores nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TPOST3"
cat = "TPCAT3"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Post Category")
    before = len(db.transactions.list())
    cases = [
        ("TPNOACCT", cat, "1.00", "2026-04-01"),
        (acct, "TPNOCAT", "1.00", "2026-04-01"),
        (acct, cat, "1.234", "2026-04-01"),
        (acct, cat, "0", "2026-04-01"),
        (acct, cat, "1.00", "2026-02-30"),
        (acct, cat, "1.00", "not-a-date"),
    ]
    for args in cases:
        code, out, err = cli_runner("txn", "post", *args)
        print(args, code, err)
        assert code == 3
        assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-rejects-invalid ===

=== AC txn-post-negative-balance ===
Intent: A payment larger than the account balance exits 3 and stores nothing, while a payment within the balance succeeds.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TPOST4"
cat = "TPCAT4"
with db_session() as db:
    db.accounts.create(account=acct, name="Post Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Post Category")
    start = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=start, date="2026-04-01", account=acct, category=cat, amount=1000, memo="seed"
    )
    before = len(db.transactions.list(account=acct))
    code, out, err = cli_runner("txn", "post", acct, cat, "-10.01", "2026-04-02")
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert len(db.transactions.list(account=acct)) == before
    code, out, err = cli_runner("txn", "post", acct, cat, "-5.00", "2026-04-02")
    print(out)
    print(err)
    assert code == 0
    rows = db.transactions.list(account=acct)
    assert len(rows) == before + 1
    assert sum(r.amount for r in rows) == 500
=== END AC txn-post-negative-balance ===

=== AC txn-post-usage ===
Intent: Too few or too many arguments exit 2 and store nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    before = len(db.transactions.list())
    code, out, err = cli_runner("txn", "post", "TPOST5", "TPCAT5", "1.00")
    assert code == 2
    assert out == ""
    code, out, err = cli_runner("txn", "post", "A", "B", "1.00", "2026-04-01", "m", "extra")
    assert code == 2
    assert out == ""
    assert len(db.transactions.list()) == before
=== END AC txn-post-usage ===

## User Acceptance

- None.

## Guardrails

- Every input and the resulting balance are checked before the first write; a rejected post stores nothing.
- Amounts are integer cents at every layer; floating point is never used for money.
- The next `txn_id` is computed from stored rows, never from a counter or constant.
- Diagnostics go to standard error only; standard output carries CSV on success and nothing on failure.
