# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | The `ledger account get` command that shows one account with its transaction count and computed balance. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger account get |
| Consumes | ledger, accounts, transactions |

## Purpose

Register `get <code>` in the `account` group. It also supplies the shared account-row builder used by
`add`, `rename`, and the balances report: the transaction count and the balance are computed from the
account's stored transactions in integer cents.

## Behavior

- Exactly one argument after `get`; any other count is a usage error, exit 2.
- An absent account exits 4 with empty standard output.
- Success writes `account,name,transactions,balance` then the account row. `transactions` is the
  number of the account's transactions; `balance` is the sum of their amounts written with exactly two
  decimals and a leading `-` when negative.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: fetch the account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-005` — read: list the account's transactions to count and sum - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC account-get-empty-account ===
Intent: Getting an account with no transactions writes its header and row with count 0 and balance 0.00.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code_val = "ZQAG1"
name = "Empty Box"
with db_session() as db:
    db.accounts.create(account=code_val, name=name)
    code, out, err = cli_runner("account", "get", code_val)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(io.StringIO(out)))
    assert parsed == [
        ["account", "name", "transactions", "balance"],
        [code_val, name, "0", "0.00"],
    ]
=== END AC account-get-empty-account ===

=== AC account-get-computed-balance ===
Intent: The transaction count and balance come from stored transactions, derived here from the cents that were inserted.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

code_val = "ZQAG2"
name = "Busy Box"
cat = "ZQAG2"
amounts = [1250, -300, 5]
with db_session() as db:
    db.accounts.create(account=code_val, name=name)
    db.categories.create(category=cat, description="Get")
    for i, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=920001 + i, date="2026-05-01", account=code_val, category=cat,
            amount=cents, memo="",
        )
    code, out, err = cli_runner("account", "get", code_val)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(io.StringIO(out)))
    want_balance = str((Decimal(sum(amounts)) / 100).quantize(Decimal("0.01")))
    assert parsed[0] == ["account", "name", "transactions", "balance"]
    assert parsed[1] == [code_val, name, str(len(amounts)), want_balance]
=== END AC account-get-computed-balance ===

=== AC account-get-absent ===
Intent: Getting an account that was never stored exits 4 with empty stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

absent = "ZQNOSUCH"
with db_session() as db:
    assert db.accounts.get(account=absent) is None
    code, out, err = cli_runner("account", "get", absent)
    print(out, err)
    assert code == 4
    assert out == ""
=== END AC account-get-absent ===

=== AC account-get-after-add ===
Intent: An account created through account add is returned unchanged by account get on a separate invocation.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

code_val = "ZQAG3"
name = "Round Trip"
with db_session():
    code, out, err = cli_runner("account", "add", code_val, name)
    assert code == 0
    added = list(csv.reader(io.StringIO(out)))
    code, out, err = cli_runner("account", "get", code_val)
    print(out, err)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == added
=== END AC account-get-after-add ===

=== AC account-get-usage ===
Intent: Missing or surplus arguments to account get exit 2 with empty stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session():
    for args in (("account", "get"), ("account", "get", "ZQAG4", "extra")):
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
=== END AC account-get-usage ===

## User Acceptance

- None.

## Guardrails

- `account get` writes nothing to the store.
- Balances are summed in integer cents and formatted with exactly two decimals; no floating point.
- Persistence is reached only through the `persistence` package.
