# FEATURE: Report Balances

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger report balances`, listing each account's transaction count and balance plus a TOTAL row. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger report balances |

## Purpose

`ledger report balances` prints one row per account with its transaction count and balance, ordered
by account code, followed by a TOTAL row. Every value is computed from the database at run time;
nothing is stored or hard-coded.

## Behavior

- Header row: `account,name,transactions,balance`.
- One data row per account, ordered by account code, including accounts with no transactions
  (count `0`, balance `0.00`).
- Final row: `TOTAL,,<count>,<sum>` where count is the total number of transactions and sum is the
  total of all balances.
- Balances are sums of integer cents, written with exactly two decimal places, a leading `-` when
  negative, and no thousands separator.
- Output is unquoted CSV with `\n` line endings; exit `0`.

## Database Interface

- `FEATURE-ACCOUNT-002` — read: list every account in code order - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: list an account's transactions to count and sum them - supplies: `account` - returns: `account`, `amount`

## Programmatic Acceptance

=== AC report-balances-rows ===
Intent: The report has one row per stored account in code order with counts and balances computed from stored transactions, then a consistent TOTAL row.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

def cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text), text
    return int(Decimal(text) * 100)

with db_session() as db:
    cat = "ACPTRBC"
    db.accounts.create(account="ACPTRB1", name="Report One")
    db.accounts.create(account="ACPTRB2", name="Report Two")
    db.categories.create(category=cat, description="Report Category")
    base = max([t.txn_id for t in db.transactions.list()], default=0)
    db.transactions.create(txn_id=base + 1, date="2026-06-01", account="ACPTRB1", category=cat, amount=10000, memo="")
    db.transactions.create(txn_id=base + 2, date="2026-06-02", account="ACPTRB1", category=cat, amount=-1250, memo="")
    db.transactions.create(txn_id=base + 3, date="2026-06-03", account="ACPTRB2", category=cat, amount=500000, memo="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    data = rows[1:-1]
    total = rows[-1]
    accounts = db.accounts.list()
    assert [r[0] for r in data] == [a.account for a in accounts]
    assert [r[0] for r in data] == sorted(r[0] for r in data)
    count_sum = 0
    cents_sum = 0
    for row, acct in zip(data, accounts):
        assert len(row) == 4
        txns = db.transactions.list(account=acct.account)
        assert row[1] == acct.name
        assert int(row[2]) == len(txns)
        assert cents(row[3]) == sum(t.amount for t in txns)
        count_sum += len(txns)
        cents_sum += sum(t.amount for t in txns)
    assert total[0] == "TOTAL"
    assert total[1] == ""
    assert len(total) == 4
    assert int(total[2]) == count_sum
    assert cents(total[3]) == cents_sum
=== END AC report-balances-rows ===

=== AC report-balances-empty-account ===
Intent: An account with no transactions appears with a zero count and a zero balance.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    acct = "ACPTRE1"
    db.accounts.create(account=acct, name="Empty Report")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    mine = [r for r in rows[1:-1] if r[0] == acct]
    assert len(mine) == 1
    assert int(mine[0][2]) == 0
    assert re.fullmatch(r"-?\d+\.\d{2}", mine[0][3])
    assert int(Decimal(mine[0][3]) * 100) == 0
=== END AC report-balances-empty-account ===

=== AC report-balances-reflects-changes ===
Intent: The report is computed from the database, so a new transaction changes the reported balance by its amount.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

def balance_of(out, acct):
    rows = list(csv.reader(io.StringIO(out)))
    mine = [r for r in rows[1:-1] if r[0] == acct]
    assert len(mine) == 1
    assert re.fullmatch(r"-?\d+\.\d{2}", mine[0][3])
    return int(Decimal(mine[0][3]) * 100), int(mine[0][2])

with db_session() as db:
    acct = "ACPTRC1"
    cat = "ACPTRCC"
    db.accounts.create(account=acct, name="Changing Report")
    db.categories.create(category=cat, description="Changing Category")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    first_balance, first_count = balance_of(out, acct)
    delta = 123456
    tid = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=tid, date="2026-06-04", account=acct, category=cat, amount=delta, memo="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    second_balance, second_count = balance_of(out, acct)
    assert second_balance == first_balance + delta
    assert second_count == first_count + 1
=== END AC report-balances-reflects-changes ===

## User Acceptance

- None.

## Guardrails

- No balance, count, or total is hard-coded; every value comes from a query at run time.
- Amounts are integer cents internally and never floating point.
- The report writes nothing to the database.
