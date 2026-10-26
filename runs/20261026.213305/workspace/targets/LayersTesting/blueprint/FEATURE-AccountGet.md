# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger account get <code>` printing an account with its transaction count and balance. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-AccountAdd.md, FEATURE-CsvOutput.md, FEATURE-ErrorContract.md |
| Provides | ledger account get |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, ledger_errors.NotFound |

## Purpose

`ledger account get <code>` prints the current account row, with the transaction count and balance computed from stored transactions at the time of the call.

## Behavior

- Argument: exactly one code; any other count is a usage error (exit 2).
- Writes `account,name,transactions,balance` then the row. `transactions` is the number of the account's transactions; `balance` is the sum of their amounts in integer cents, written with exactly two decimals, a leading `-` when negative, and `0.00` for zero.
- An absent code exits 4 with nothing on standard output.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: get an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-003` — read: list the account's transactions to count and sum them - supplies: `account` - returns: `txn_id`, `account`, `amount`

## Programmatic Acceptance

=== AC account-get-with-activity ===
Intent: The printed transaction count and balance are computed from the stored transactions.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZAG1A", "ZAG1C"
name = "Get Account"
amounts = [50000, -12550, 325]
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    db.categories.create(category=cat, description="Get test")
    for i, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=920001 + i, date="2026-05-01", account=acct, category=cat, amount=cents, memo=""
        )
    code, out, err = cli_runner("account", "get", acct)
    print(out, err)
    assert code == 0
    balance = f"{Decimal(sum(amounts)).scaleb(-2):.2f}"
    assert list(csv.reader(io.StringIO(out))) == [
        ["account", "name", "transactions", "balance"],
        [acct, name, str(len(amounts)), balance],
    ]
=== END AC account-get-with-activity ===

=== AC account-get-no-activity ===
Intent: An account without transactions prints a zero count and balance 0.00.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZAG2A"
name = "Quiet Account"
with db_session() as db:
    db.accounts.create(account=acct, name=name)
    code, out, err = cli_runner("account", "get", acct)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [
        ["account", "name", "transactions", "balance"],
        [acct, name, "0", "0.00"],
    ]
=== END AC account-get-no-activity ===

=== AC account-get-reflects-changes ===
Intent: A later get reflects a new transaction, so the values are read from storage rather than remembered.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct, cat = "ZAG3A", "ZAG3C"
with db_session() as db:
    db.accounts.create(account=acct, name="Changing")
    db.categories.create(category=cat, description="Get test")
    code, out, err = cli_runner("account", "get", acct)
    assert code == 0
    first = list(csv.reader(io.StringIO(out)))[1]
    assert first[2] == "0"
    cents = 4242
    db.transactions.create(txn_id=920011, date="2026-05-02", account=acct, category=cat, amount=cents, memo="")
    code, out, err = cli_runner("account", "get", acct)
    print(out, err)
    assert code == 0
    second = list(csv.reader(io.StringIO(out)))[1]
    assert second[2] == "1"
    assert second[3] == f"{Decimal(cents).scaleb(-2):.2f}"
=== END AC account-get-reflects-changes ===

=== AC account-get-absent ===
Intent: An absent account exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "ZAG4NONE"
with db_session() as db:
    assert db.accounts.get(account=absent) is None
    code, out, err = cli_runner("account", "get", absent)
    print(code, out, err)
    assert code == 4
    assert out == ""
=== END AC account-get-absent ===

=== AC account-get-wrong-argument-count ===
Intent: A wrong argument count is a usage error with exit 2.

from cli.testing import cli_runner

for args in (("account", "get"), ("account", "get", "ZAG5A", "extra")):
    code, out, err = cli_runner(*args)
    print(args, code, out, err)
    assert code == 2
    assert out == ""
=== END AC account-get-wrong-argument-count ===

## User Acceptance

- None.

## Guardrails

- The command is read-only and never writes to the database.
- Count and balance come from stored transactions, never from embedded values.
- Balances are integer cents internally; no floating point at any layer.
