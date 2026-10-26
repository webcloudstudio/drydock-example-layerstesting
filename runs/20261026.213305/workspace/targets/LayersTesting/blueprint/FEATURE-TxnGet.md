# FEATURE: Txn Get

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger txn get <id>`, which prints one stored transaction row. |
| Depends On | FEATURE-TxnPost.md, FEATURE-CsvOutput.md, FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger txn get |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound |

## Purpose

Read back a single transaction by id from stored data.

## Behavior

- Invocation: `ledger txn get <id>` with exactly one argument.
- A non-integer id exits 3 (narrowest reading of the unspecified case, recorded as decision Q-003).
- An integer id with no stored row exits 4 with nothing on stdout.
- Otherwise the command writes the header `txn_id,date,account,category,amount,memo` and the stored row, with the amount formatted as exactly two decimals from integer cents.

## Database Interface

- `FEATURE-TXN-002` — read: get the transaction by id - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-get-present ===
Intent: Getting a stored transaction prints its current row with a two-decimal amount.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQGET1"
cat = "ZQGETC1"
txn_id = 920001
date = "2026-04-01"
cents = -1234
memo = "read me"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=cents, memo=memo
    )
    code, out, err = cli_runner("txn", "get", str(txn_id))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    shown = f"{Decimal(cents) / 100:.2f}"
    assert rows[1] == [str(txn_id), date, acct, cat, shown, memo]
=== END AC txn-get-present ===

=== AC txn-get-empty-memo ===
Intent: A transaction with an empty memo prints an empty final field.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQGET2"
cat = "ZQGETC2"
txn_id = 920002
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-02", account=acct, category=cat, amount=500, memo=""
    )
    code, out, err = cli_runner("txn", "get", str(txn_id))
    print(out)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows[1]) == 6
    assert rows[1][5] == ""
=== END AC txn-get-empty-memo ===

=== AC txn-get-absent ===
Intent: An absent id exits 4 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    ids = [r.txn_id for r in db.transactions.list()]
    absent = (max(ids) if ids else 0) + 1000
    code, out, err = cli_runner("txn", "get", str(absent))
    print(err)
    assert code == 4
    assert out == ""
=== END AC txn-get-absent ===

=== AC txn-get-non-integer ===
Intent: A non-integer id exits 3 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    for bad in ("abc", "1.5", "-"):
        code, out, err = cli_runner("txn", "get", bad)
        assert code == 3, bad
        assert out == "", bad
=== END AC txn-get-non-integer ===

=== AC txn-get-after-delete ===
Intent: After the row is removed the same id is reported absent.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQGET3"
cat = "ZQGETC3"
txn_id = 920003
with db_session() as db:
    db.accounts.create(account=acct, name="Get Account")
    db.categories.create(category=cat, description="Get Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-03", account=acct, category=cat, amount=100, memo="x"
    )
    code, out, err = cli_runner("txn", "get", str(txn_id))
    assert code == 0
    db.transactions.delete(txn_id=txn_id)
    code, out, err = cli_runner("txn", "get", str(txn_id))
    assert code == 4
    assert out == ""
=== END AC txn-get-after-delete ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never writes to the database.
- A failing command writes nothing to stdout and never echoes a DSN or credential.
