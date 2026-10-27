# FEATURE: Transaction Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn get <id>` printing one stored transaction row. |
| Depends On | FEATURE-TxnPost.md, DATABASE.md |
| Provides | ledger txn get |
| Consumes | ledger txn post |

## Purpose

Read one transaction by id through the `txn` verb table in `cli/commands/txn.py`.

## Behavior

1. Usage: `ledger txn get <id>`; any other argument count is a usage error (exit 2).
2. An id that is not a string of decimal digits is rejected with exit 3.
3. An absent id exits 4 with nothing on standard output.
4. Otherwise print the header `txn_id,date,account,category,amount,memo` and the stored row, amount with two decimals.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-get-success ===
Intent: Get prints the header and the stored row, with the amount rendered from integer cents.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTGET1"
cat = "ZZTGCAT1"
date = "2026-04-10"
memo = "get me"
amount_cents = 1250
amount_text = "12.50"
with db_session() as db:
    db.accounts.create(account=acct, name="Get One")
    db.categories.create(category=cat, description="Get Cat")
    txn_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=amount_cents, memo=memo
    )
    exit_code, out, err = cli_runner("txn", "get", str(txn_id))
    print(out)
    print(err)
    assert exit_code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), date, acct, cat, amount_text, memo]
    assert len(rows) == 2
=== END AC txn-get-success ===

=== AC txn-get-negative-amount ===
Intent: A negative stored amount prints with a leading minus and two decimals.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTGET2"
cat = "ZZTGCAT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Two")
    db.categories.create(category=cat, description="Get Cat Two")
    first_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=first_id, date="2026-04-11", account=acct, category=cat, amount=2000, memo="in"
    )
    out_id = first_id + 1
    db.transactions.create(
        txn_id=out_id, date="2026-04-12", account=acct, category=cat, amount=-1234, memo="out"
    )
    exit_code, out, err = cli_runner("txn", "get", str(out_id))
    print(out, err)
    assert exit_code == 0
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[4] == "-12.34"
=== END AC txn-get-negative-amount ===

=== AC txn-get-absent ===
Intent: An id no transaction holds exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    missing = max([r.txn_id for r in db.transactions.list()], default=0) + 1000
    assert db.transactions.get(txn_id=missing) is None
    exit_code, out, err = cli_runner("txn", "get", str(missing))
    print(out)
    print(err)
    assert exit_code == 4
    assert out == ""
=== END AC txn-get-absent ===

=== AC txn-get-non-digit-id ===
Intent: Ids that are not strings of decimal digits are rejected with exit 3 and nothing on standard output.

from cli.testing import cli_runner

for bad in ("abc", "-1", "1.5", "1e3"):
    exit_code, out, err = cli_runner("txn", "get", bad)
    print(bad, exit_code, out, err)
    assert exit_code == 3
    assert out == ""
=== END AC txn-get-non-digit-id ===

=== AC txn-get-usage ===
Intent: Calling get with no id is a usage error with exit 2.

from cli.testing import cli_runner

exit_code, out, err = cli_runner("txn", "get")
print(out)
print(err)
assert exit_code == 2
assert out == ""
=== END AC txn-get-usage ===

## User Acceptance

- None.

## Guardrails

- Get is read-only and never writes.
- Diagnostics go to standard error only.
