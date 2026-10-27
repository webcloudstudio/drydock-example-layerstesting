# FEATURE: Report Balances

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report balances`, one row per account with its transaction count and balance computed from stored transactions. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-LedgerCli.md, DATABASE.md |
| Provides | ledger report balances |
| Consumes | ledger, accounts, transactions |

## Purpose

Report the cash held in each account. Every value is computed from stored rows at the time of the command; nothing is embedded.

## Interface

`ledger report balances`

Standard output on success (exit 0), CSV with `\n` endings and no quoting:

- header `account,name,transactions,balance`
- one row per account ordered by code ascending
- final row `TOTAL,,<count>,<sum>`, where `<count>` is the total number of transactions and `<sum>` the sum of all balances

## Behavior

1. Read accounts with `db.accounts.list` and each account's transactions with `db.transactions.list(account=...)`.
2. Balance is the sum of integer cents; the count is the number of the account's transactions.
3. Write balances with exactly two decimals, a leading `-` when negative, and no thousands separator.
4. An empty ledger writes the header and `TOTAL,,0,0.00`.
5. The command is read-only.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-balances-rows ===
Intent: The balances report lists every account in code order with count and balance derived from the stored transactions, followed by a TOTAL row, and the report writes no record.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

cat = "ZQRC"
with db_session() as db:
    db.accounts.create(account="ZQR2", name="Second Account")
    db.accounts.create(account="ZQR1", name="First Account")
    db.categories.create(category=cat, description="Report Cat")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account="ZQR1", category=cat, amount=120050, memo="")
    db.transactions.create(txn_id=base + 1, date="2026-06-02", account="ZQR1", category=cat, amount=-2500, memo="")
    db.transactions.create(txn_id=base + 2, date="2026-06-03", account="ZQR2", category=cat, amount=75000, memo="")
    count_before = len(db.transactions.list())
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    assert "\r" not in out
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    expected = []
    for a in sorted(db.accounts.list(), key=lambda r: r.account):
        txns = db.transactions.list(account=a.account)
        expected.append((a.account, a.name, len(txns), sum(t.amount for t in txns)))
    data = rows[1:-1]
    assert len(data) == len(expected)
    for row, (acct_code, name, n, bal) in zip(data, expected):
        assert row[0] == acct_code
        assert row[1] == name
        assert int(row[2]) == n
        assert Decimal(row[3]) == Decimal(bal).scaleb(-2)
        assert re.fullmatch(r"-?\d+\.\d{2}", row[3])
    codes = [r[0] for r in data]
    assert codes.index("ZQR1") < codes.index("ZQR2")
    total = rows[-1]
    assert total[0] == "TOTAL"
    assert total[1] == ""
    assert int(total[2]) == sum(e[2] for e in expected)
    assert Decimal(total[3]) == Decimal(sum(e[3] for e in expected)).scaleb(-2)
    assert re.fullmatch(r"-?\d+\.\d{2}", total[3])
    assert len(db.transactions.list()) == count_before
=== END AC report-balances-rows ===

=== AC report-balances-empty-ledger ===
Intent: With no accounts or transactions the report writes only its header and a zero TOTAL row.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    db.transactions.delete_all(min_txn_id=0)
    db.categories.delete_all(min_category="")
    db.accounts.delete_all(min_account="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["account", "name", "transactions", "balance"], ["TOTAL", "", "0", "0.00"]]
=== END AC report-balances-empty-ledger ===

=== AC report-balances-negative-and-account-without-rows ===
Intent: An account with no transactions reports a zero count and a 0.00 balance, and balances follow later changes made through the store.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

cat = "ZQRD"
with db_session() as db:
    db.accounts.create(account="ZQR3", name="Empty Account")
    db.accounts.create(account="ZQR4", name="Funded Account")
    db.categories.create(category=cat, description="Report Cat")
    base = max([r.txn_id for r in db.transactions.list()] or [0]) + 1
    db.transactions.create(txn_id=base, date="2026-06-01", account="ZQR4", category=cat, amount=1234, memo="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    by_code = {r[0]: r for r in csv.reader(io.StringIO(out))}
    assert int(by_code["ZQR3"][2]) == 0
    assert Decimal(by_code["ZQR3"][3]) == 0
    assert int(by_code["ZQR4"][2]) == 1
    assert Decimal(by_code["ZQR4"][3]) == Decimal(1234).scaleb(-2)
    db.transactions.update(txn_id=base, amount=4321)
    code, out, err = cli_runner("report", "balances")
    print(out)
    assert code == 0
    by_code = {r[0]: r for r in csv.reader(io.StringIO(out))}
    assert Decimal(by_code["ZQR4"][3]) == Decimal(4321).scaleb(-2)
=== END AC report-balances-negative-and-account-without-rows ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query; no row, count, or total is hardcoded.
- Amounts are integer cents; no floating point.
- The report writes nothing to the store.
