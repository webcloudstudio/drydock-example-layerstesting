# FEATURE: Txn Get

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `ledger txn get` command prints one stored transaction row by id. |
| Depends On  | FEATURE-CliFoundation.md, DATABASE.md |
| Provides    | ledger txn get |
| Consumes    | transactions.get |

## Purpose

`ledger txn get <id>` shows one stored transaction so an operator can confirm what was recorded.

## Trigger

An operator runs `./ledger txn get <id>`.

## Sequence

1. Reject a wrong argument count with exit 2.
2. Reject an id that is not an integer with exit 3.
3. Read the row with `transactions.get`. An absent id exits 4.
4. Print the header row and the row, with the amount written with exactly two decimals. Exit 0.

## Output

```text
txn_id,date,account,category,amount,memo
<id>,<date>,<account>,<category>,<amount with two decimals>,<memo>
```

## Reads

- `transactions.get`

## Writes

- None.

## Database Interface

- `FEATURE-TRANSACTIONS-002` — read: retrieve a transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-present ===
Intent: Getting a stored transaction prints its header and a row carrying the stored values with a two-decimal amount.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TGET1"
cat = "TGCAT1"
when = "2026-04-01"
memo = "get probe"
deposit_cents = 1234
deposit_text = "12.34"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Get Category")
    txn_id = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=txn_id, date=when, account=acct, category=cat, amount=deposit_cents, memo=memo
    )
    code, out, err = cli_runner("txn", "get", str(txn_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), when, acct, cat, deposit_text, memo]
    assert len(rows) == 2
=== END AC txn-get-present ===

=== AC txn-get-negative-amount ===
Intent: A negative stored amount prints with a leading minus sign and two decimals.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "TGET2"
cat = "TGCAT2"
cents = -1250
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    if db.categories.get(category=cat) is None:
        db.categories.create(category=cat, description="Get Category")
    txn_id = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=cents, memo=""
    )
    code, out, err = cli_runner("txn", "get", str(txn_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    shown = rows[1][4]
    assert shown.startswith("-")
    assert len(shown.split(".")[1]) == 2
    assert Decimal(shown) * 100 == cents
=== END AC txn-get-negative-amount ===

=== AC txn-get-absent ===
Intent: Getting an id that is not stored exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    absent = max([r.txn_id for r in db.transactions.list()] or [0]) + 1000
    code, out, err = cli_runner("txn", "get", str(absent))
    print(err)
    assert code == 4
    assert out == ""
=== END AC txn-get-absent ===

=== AC txn-get-bad-arguments ===
Intent: A non-integer id exits 3 and a wrong argument count exits 2.

from cli.testing import cli_runner

code, out, err = cli_runner("txn", "get", "abc")
assert code == 3
assert out == ""
code, out, err = cli_runner("txn", "get")
assert code == 2
assert out == ""
code, out, err = cli_runner("txn", "get", "1", "2")
assert code == 2
assert out == ""
=== END AC txn-get-bad-arguments ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never writes.
- The amount is formatted from integer cents without floating point.
- Diagnostics go to standard error only.
