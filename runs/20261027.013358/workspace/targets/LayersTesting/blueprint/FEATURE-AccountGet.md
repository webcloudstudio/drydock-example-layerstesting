# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account get <code>` printing the current account row with computed transaction count and balance. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-LedgerRules.md, DATABASE.md |
| Provides | ledger account get |
| Consumes | ledger account add, ledgerlib.rules |

## Purpose

Show one account with its live transaction count and balance computed from stored transactions.

## Interface

`ledger account get <code>`. Output:

```text
account,name,transactions,balance
<code>,<name>,<count>,<balance>
```

`balance` is the sum of the account's transaction amounts, written with exactly two decimals from integer cents.

## Behavior

1. `get` with other than exactly one argument is a usage error (exit 2).
2. An absent code is not found (exit 4) with nothing on stdout.
3. Count and balance are computed at run time from the account's stored transactions only.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC acct-get-empty-account ===
Intent: An account with no transactions prints count 0 and balance 0.00.

import csv
from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZAG1"
name = "Get Empty"
with db_session() as db:
    db.accounts.create(account=code_arg, name=name)
    code, out, err = cli_runner("account", "get", code_arg)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed == [["account", "name", "transactions", "balance"], [code_arg, name, "0", "0.00"]]
=== END AC acct-get-empty-account ===

=== AC acct-get-with-transactions ===
Intent: Count and balance reflect only this account's stored transactions, with the balance formatted from the integer cents sum.

import csv
from cli.testing import cli_runner
from persistence.testing import db_session

mine = "ZZAG2"
other = "ZZAG3"
cat = "ZZAGC1"
name = "Get Busy"
amounts = [12345, -2000, 500]
other_amounts = [99999]
with db_session() as db:
    db.accounts.create(account=mine, name=name)
    db.accounts.create(account=other, name="Get Other")
    db.categories.create(category=cat, description="Get Cat")
    tid = 870001
    for amount in amounts:
        db.transactions.create(txn_id=tid, date="2026-04-01", account=mine, category=cat, amount=amount, memo="m")
        tid += 1
    for amount in other_amounts:
        db.transactions.create(txn_id=tid, date="2026-04-01", account=other, category=cat, amount=amount, memo="o")
        tid += 1
    total = sum(amounts)
    assert total >= 0
    expected_balance = f"{total // 100}.{total % 100:02d}"
    code, out, err = cli_runner("account", "get", mine)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed[0] == ["account", "name", "transactions", "balance"]
    assert parsed[1] == [mine, name, str(len(amounts)), expected_balance]
=== END AC acct-get-with-transactions ===

=== AC acct-get-reflects-changes ===
Intent: A later get returns current values after another transaction is stored, not a cached earlier result.

import csv
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZAG4"
cat = "ZZAGC2"
with db_session() as db:
    db.accounts.create(account=acct, name="Get Fresh")
    db.categories.create(category=cat, description="Get Cat2")
    db.transactions.create(txn_id=870011, date="2026-04-01", account=acct, category=cat, amount=1000, memo="a")
    code1, out1, err1 = cli_runner("account", "get", acct)
    db.transactions.create(txn_id=870012, date="2026-04-02", account=acct, category=cat, amount=250, memo="b")
    code2, out2, err2 = cli_runner("account", "get", acct)
    print(out1, err1, out2, err2)
    assert code1 == 0 and code2 == 0
    row1 = list(csv.reader(out1.splitlines()))[1]
    row2 = list(csv.reader(out2.splitlines()))[1]
    assert row1[2] == "1"
    assert row2[2] == "2"
    assert row1[3] != row2[3]
=== END AC acct-get-reflects-changes ===

=== AC acct-get-not-found ===
Intent: An absent account code exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

missing = "ZZNOSUCH1"
with db_session() as db:
    assert db.accounts.get(account=missing) is None
    code, out, err = cli_runner("account", "get", missing)
    print(out, err)
    assert code == 4
    assert out == ""
=== END AC acct-get-not-found ===

=== AC acct-get-usage ===
Intent: Missing or extra arguments to account get are usage errors with exit 2.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    for args in [("account", "get"), ("account", "get", "ZZAG5", "extra")]:
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
=== END AC acct-get-usage ===

## User Acceptance

- None.

## Guardrails

- Get never writes to the store.
- Count and balance are computed from stored transactions, never stored or hardcoded.
- Money is formatted from integer cents; no floating point.
