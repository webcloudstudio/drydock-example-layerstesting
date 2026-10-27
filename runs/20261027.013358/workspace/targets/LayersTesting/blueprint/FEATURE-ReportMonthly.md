# FEATURE: Report Monthly

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Report transaction count, inflow, outflow and net per calendar month that has transactions. |
| Depends On | FEATURE-ReportBalances.md |
| Provides | ledger report monthly |
| Consumes | ledger report balances |

## Purpose

`ledger report monthly` summarizes stored transactions per `YYYY-MM` and in total.

## Trigger

Command line: `./ledger report monthly`, added to the report-name table in
`cli/commands/report.py`. Extra arguments are a `UsageError` (exit 2).

## Output

Header `month,transactions,inflow,outflow,net`, one row per `YYYY-MM` that has at least one
transaction in ascending order, then `TOTAL,<count>,<inflow>,<outflow>,<net>`. `inflow` sums
positive amounts, `outflow` sums absolute values of negative amounts as a positive number, and
`net` is `inflow - outflow`. Money uses exactly two decimals computed from integer cents. On an
empty ledger the output is the header and `TOTAL,0,0.00,0.00,0.00`.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC monthly-report ===
Intent: Month rows are the distinct stored YYYY-MM values in ascending order with counts and amounts derived from stored transactions, and the TOTAL row matches.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

money = re.compile(r"^-?\d+\.\d\d$")
with db_session() as db:
    db.accounts.create(account="ZZRM1", name="Rpt Month Acct")
    db.categories.create(category="ZZRMCAT", description="Rpt Month")
    base = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    specs = [
        ("2099-03-05", 1000),
        ("2099-01-20", 4550),
        ("2099-01-21", -1250),
        ("2099-02-02", -300),
        ("2099-03-30", 25),
    ]
    for i, (date, cents) in enumerate(specs):
        db.transactions.create(txn_id=base + i, date=date, account="ZZRM1", category="ZZRMCAT", amount=cents, memo="rm")
    code, out, err = cli_runner("report", "monthly")
    print(out)
    print(err)
    assert code == 0
    assert out.endswith("\n")
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["month", "transactions", "inflow", "outflow", "net"]
    txns = db.transactions.list()
    months = sorted({t.date[:7] for t in txns})
    data, total = rows[1:-1], rows[-1]
    assert [r[0] for r in data] == months
    for r, month in zip(data, months):
        amounts = [t.amount for t in txns if t.date[:7] == month]
        inflow = sum(a for a in amounts if a > 0)
        outflow = -sum(a for a in amounts if a < 0)
        assert len(r) == 5
        assert int(r[1]) == len(amounts)
        for field in r[2:]:
            assert money.match(field)
        assert Decimal(r[2]) == Decimal(inflow) / 100
        assert Decimal(r[3]) == Decimal(outflow) / 100
        assert Decimal(r[4]) == Decimal(inflow - outflow) / 100
    all_amounts = [t.amount for t in txns]
    t_in = sum(a for a in all_amounts if a > 0)
    t_out = -sum(a for a in all_amounts if a < 0)
    assert len(total) == 5
    assert total[0] == "TOTAL"
    assert int(total[1]) == len(txns)
    assert Decimal(total[2]) == Decimal(t_in) / 100
    assert Decimal(total[3]) == Decimal(t_out) / 100
    assert Decimal(total[4]) == Decimal(t_in - t_out) / 100
=== END AC monthly-report ===

=== AC monthly-computed-from-storage ===
Intent: Adding a transaction in a new month adds that month row with exactly that amount and raises the TOTAL count by one.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

month = "2098-07"
delta = 4200
with db_session() as db:
    db.accounts.create(account="ZZRMS1", name="Rpt Month Store")
    db.categories.create(category="ZZRMSCAT", description="Rpt Month Store")

    def snapshot():
        code, out, err = cli_runner("report", "monthly")
        print(out, err)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        return rows[1:-1], rows[-1]

    data_before, total_before = snapshot()
    assert month not in [r[0] for r in data_before]
    new_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date=month + "-15", account="ZZRMS1", category="ZZRMSCAT", amount=delta, memo="rms")
    data_after, total_after = snapshot()
    mine = [r for r in data_after if r[0] == month]
    assert len(mine) == 1
    assert int(mine[0][1]) == 1
    assert Decimal(mine[0][2]) == Decimal(delta) / 100
    assert Decimal(mine[0][3]) == 0
    assert Decimal(mine[0][4]) == Decimal(delta) / 100
    assert int(total_after[1]) == int(total_before[1]) + 1
    months = [r[0] for r in data_after]
    assert months == sorted(months)
=== END AC monthly-computed-from-storage ===

=== AC monthly-usage ===
Intent: Extra arguments to the monthly report exit 2 with empty stdout.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "monthly", "extra")
print(code, out, err)
assert code == 2
assert out == ""
assert err.strip() != ""
=== END AC monthly-usage ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query at run time; no month, count or total is hardcoded.
- Only months that have transactions appear.
- Money is integer cents; no floating point at any layer.
- The report never writes to the database.
