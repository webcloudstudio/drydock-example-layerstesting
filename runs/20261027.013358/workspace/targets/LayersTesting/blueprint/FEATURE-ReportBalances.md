# FEATURE: Report Balances

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Report each account's transaction count and balance, plus a total row, computed from stored data. |
| Depends On | FEATURE-LedgerRules.md, FEATURE-LoadTransactions.md, FEATURE-CsvOutput.md |
| Provides | ledger report balances |
| Consumes | ledgerlib.rules, ledgerlib.csvout |

## Purpose

`ledger report balances` prints one row per account ordered by code, then a `TOTAL` row. It also
creates the report dispatcher used by the other reports.

## Trigger

Command line: `./ledger report balances`. Implemented in `cli/commands/report.py`, which holds a
report-name table. An unknown report name, a missing name, or extra arguments is a `UsageError`
(exit 2) raised before any database access.

## Output

Header `account,name,transactions,balance`, then per account (ordered by code) the account code,
name, the count of its transactions, and its balance. Final row `TOTAL,,<count>,<sum>` where
`<count>` is the total number of stored transactions and `<sum>` the total of all balances.
Money is formatted from integer cents with exactly two decimals and never prints as `-0.00`.
On an empty ledger the output is the header and `TOTAL,,0,0.00`.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC balances-report ===
Intent: Balances rows follow stored accounts in code order with counts and two-decimal balances derived from stored transactions, and a zero balance prints as 0.00.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

money = re.compile(r"^-?\d+\.\d\d$")
with db_session() as db:
    db.categories.create(category="ZZRBCAT", description="Rpt Bal")
    db.accounts.create(account="ZZRB1", name="Rpt One")
    db.accounts.create(account="ZZRB2", name="Rpt Two")
    db.accounts.create(account="ZZRB3", name="Rpt Zero")
    base = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    specs = [("ZZRB1", 12345), ("ZZRB1", -2000), ("ZZRB2", 50), ("ZZRB3", 700), ("ZZRB3", -700)]
    for i, (acct, cents) in enumerate(specs):
        db.transactions.create(txn_id=base + i, date="2099-01-15", account=acct, category="ZZRBCAT", amount=cents, memo="rb")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    assert out.endswith("\n")
    assert '"' not in out and "\r" not in out
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    accounts = db.accounts.list()
    txns = db.transactions.list()
    data, total = rows[1:-1], rows[-1]
    assert [r[0] for r in data] == [a.account for a in accounts]
    for r, a in zip(data, accounts):
        mine = [t.amount for t in txns if t.account == a.account]
        assert len(r) == 4
        assert r[1] == a.name
        assert int(r[2]) == len(mine)
        assert money.match(r[3])
        assert Decimal(r[3]) == Decimal(sum(mine)) / 100
    assert len(total) == 4
    assert total[0] == "TOTAL" and total[1] == ""
    assert int(total[2]) == len(txns)
    assert money.match(total[3])
    assert Decimal(total[3]) == Decimal(sum(t.amount for t in txns)) / 100
    zero = [r for r in data if r[0] == "ZZRB3"][0]
    assert zero[3] == "0.00"
    assert all(r[3] != "-0.00" for r in data)
=== END AC balances-report ===

=== AC balances-computed-from-storage ===
Intent: The report reflects stored data: adding one transaction changes the account row and the total by exactly that amount.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZZRBS1"
delta = 2575
with db_session() as db:
    db.categories.create(category="ZZRBSCAT", description="Rpt Bal Store")
    db.accounts.create(account=acct, name="Rpt Store")

    def snapshot():
        code, out, err = cli_runner("report", "balances")
        print(out, err)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        mine = [r for r in rows[1:-1] if r[0] == acct][0]
        return Decimal(mine[3]), int(mine[2]), Decimal(rows[-1][3]), int(rows[-1][2])

    acct_before, count_before, total_before, total_count_before = snapshot()
    new_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date="2099-02-01", account=acct, category="ZZRBSCAT", amount=delta, memo="rbs")
    acct_after, count_after, total_after, total_count_after = snapshot()
    assert acct_after - acct_before == Decimal(delta) / 100
    assert count_after == count_before + 1
    assert total_after - total_before == Decimal(delta) / 100
    assert total_count_after == total_count_before + 1
=== END AC balances-computed-from-storage ===

=== AC balances-usage ===
Intent: A missing, unknown or over-long report invocation exits 2 with empty stdout and changes nothing.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    before = (len(db.accounts.list()), len(db.categories.list()), len(db.transactions.list()))
    for args in [("report",), ("report", "nosuch"), ("report", "balances", "extra")]:
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
        assert err.strip() != ""
    after = (len(db.accounts.list()), len(db.categories.list()), len(db.transactions.list()))
    assert after == before
=== END AC balances-usage ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query at run time; no row, count or total is hardcoded.
- Balances and totals are computed with integer cents; no floating point at any layer.
- The report never writes to the database.
