# FEATURE: Transaction Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn get`, which writes one stored transaction row by id. |
| Depends On | FEATURE-TxnPost.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger txn get |
| Consumes | ledger, transactions |

## Purpose

Let the shop look up a single recorded transaction by its id.

## Trigger

`ledger txn get <id>` invoked from the command line.

## Sequence

1. Require exactly one argument after `get`; otherwise raise the shared usage error (exit 2).
2. Parse the id as an integer; a non-integer id exits 3.
3. Read the transaction. An absent id exits 4.
4. Write the header `txn_id,date,account,category,amount,memo` and the stored row, with the amount at exactly two decimals.

## Database Interface

- `FEATURE-TXN-002` — read: get the transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Behavior Rules

- The command never writes to the database.
- A failing command writes nothing to standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC txn-get-success ===
Intent: Getting an existing transaction exits 0 and writes its stored values with the amount formatted from the stored cents.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTG1"
cat = "ZTG1"
txn_id = 940001
date = "2026-04-01"
cents = 4550
memo = "walk in sale"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=cents, memo=memo
    )
    exit_code, out, err = cli_runner("txn", "get", str(txn_id))
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    amount_text = f"{Decimal(cents) / 100:.2f}"
    assert rows[1] == [str(txn_id), date, acct, cat, amount_text, memo]
=== END AC txn-get-success ===

=== AC txn-get-negative-and-empty-memo ===
Intent: A stored negative amount prints with a leading minus and two decimals, and an empty memo prints as an empty final field.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTG2"
cat = "ZTG2"
funding_id = 940002
txn_id = 940003
spend_cents = -1234
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(
        txn_id=funding_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo=""
    )
    db.transactions.create(
        txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=spend_cents, memo=""
    )
    exit_code, out, err = cli_runner("txn", "get", str(txn_id))
    print(exit_code, out, err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][4] == f"{Decimal(spend_cents) / 100:.2f}"
    assert len(rows[1]) == 6
    assert rows[1][5] == ""
=== END AC txn-get-negative-and-empty-memo ===

=== AC txn-get-absent ===
Intent: Getting an id that is not stored exits 4 with nothing on standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    stored = [r.txn_id for r in db.transactions.list()]
    absent = (max(stored) + 1000) if stored else 999
    exit_code, out, err = cli_runner("txn", "get", str(absent))
    print(exit_code, out, err)
    assert exit_code == 4
    assert out == ""
=== END AC txn-get-absent ===

=== AC txn-get-non-integer ===
Intent: A non-integer id is rejected with exit 3 and nothing on standard output.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    for bad in ("abc", "1.5"):
        exit_code, out, err = cli_runner("txn", "get", bad)
        print(bad, exit_code, out, err)
        assert exit_code == 3
        assert out == ""
=== END AC txn-get-non-integer ===

=== AC txn-get-after-post ===
Intent: A transaction posted through the CLI is returned unchanged by a later get, proving the post persisted.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZTG3"
cat = "ZTG3"
amount_text = "20.25"
date = "2026-04-05"
memo = "round trip"
with db_session() as db:
    db.accounts.create(account=acct, name="Round Trip")
    db.categories.create(category=cat, description="Round Trip")
    exit_code, out, err = cli_runner("txn", "post", acct, cat, amount_text, date, memo)
    print(exit_code, out, err)
    assert exit_code == 0
    posted = list(csv.reader(io.StringIO(out)))[1]
    exit_code, out, err = cli_runner("txn", "get", posted[0])
    print(exit_code, out, err)
    assert exit_code == 0
    fetched = list(csv.reader(io.StringIO(out)))[1]
    assert fetched == posted
=== END AC txn-get-after-post ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never changes a stored record.
- Persistence is reached only through the generated persistence package.
