# FEATURE: Report Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Report transaction count, inflow, outflow and net per category, including unused categories. |
| Depends On | FEATURE-ReportBalances.md |
| Provides | ledger report categories |
| Consumes | ledger report balances |

## Purpose

`ledger report categories` summarizes stored transactions per category and in total.

## Trigger

Command line: `./ledger report categories`, added to the report-name table in
`cli/commands/report.py`. Extra arguments are a `UsageError` (exit 2).

## Output

Header `category,description,transactions,inflow,outflow,net`, one row per stored category ordered
by code (categories with no transactions included with count 0 and zero amounts), then
`TOTAL,,<count>,<inflow>,<outflow>,<net>`. `inflow` is the sum of positive amounts, `outflow` the
sum of absolute values of negative amounts written as a positive number, and `net` is
`inflow - outflow`. All money uses exactly two decimals computed from integer cents.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC categories-report ===
Intent: Each category row, including an unused one, matches inflow, outflow and net derived from stored transactions, ordered by code, with a matching TOTAL row.

import csv
import io
import re
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

money = re.compile(r"^-?\d+\.\d\d$")
with db_session() as db:
    db.accounts.create(account="ZZRC1", name="Rpt Cat Acct")
    db.categories.create(category="ZZRCMIX", description="Rpt Mixed")
    db.categories.create(category="ZZRCOUT", description="Rpt Outflow")
    db.categories.create(category="ZZRCNONE", description="Rpt Unused")
    base = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    specs = [("ZZRCMIX", 10000), ("ZZRCMIX", 550), ("ZZRCMIX", -2525), ("ZZRCOUT", -799)]
    for i, (cat, cents) in enumerate(specs):
        db.transactions.create(txn_id=base + i, date="2099-03-10", account="ZZRC1", category=cat, amount=cents, memo="rc")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    assert out.endswith("\n")
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    cats = db.categories.list()
    txns = db.transactions.list()
    data, total = rows[1:-1], rows[-1]
    assert [r[0] for r in data] == [c.category for c in cats]
    for r, c in zip(data, cats):
        amounts = [t.amount for t in txns if t.category == c.category]
        inflow = sum(a for a in amounts if a > 0)
        outflow = -sum(a for a in amounts if a < 0)
        assert len(r) == 6
        assert r[1] == c.description
        assert int(r[2]) == len(amounts)
        for field in r[3:]:
            assert money.match(field)
        assert Decimal(r[3]) == Decimal(inflow) / 100
        assert Decimal(r[4]) == Decimal(outflow) / 100
        assert Decimal(r[5]) == Decimal(inflow - outflow) / 100
    unused = [r for r in data if r[0] == "ZZRCNONE"][0]
    assert int(unused[2]) == 0
    assert Decimal(unused[3]) == 0 and Decimal(unused[4]) == 0 and Decimal(unused[5]) == 0
    all_amounts = [t.amount for t in txns]
    t_in = sum(a for a in all_amounts if a > 0)
    t_out = -sum(a for a in all_amounts if a < 0)
    assert len(total) == 6
    assert total[0] == "TOTAL" and total[1] == ""
    assert int(total[2]) == len(txns)
    assert Decimal(total[3]) == Decimal(t_in) / 100
    assert Decimal(total[4]) == Decimal(t_out) / 100
    assert Decimal(total[5]) == Decimal(t_in - t_out) / 100
=== END AC categories-report ===

=== AC categories-computed-from-storage ===
Intent: Adding one inflow transaction raises that category's count and inflow and the TOTAL inflow by exactly that amount.

import csv
import io
from decimal import Decimal
from persistence.testing import db_session
from cli.testing import cli_runner

cat = "ZZRCSTO"
delta = 3333
with db_session() as db:
    db.accounts.create(account="ZZRCS1", name="Rpt Cat Store")
    db.categories.create(category=cat, description="Rpt Cat Store")

    def snapshot():
        code, out, err = cli_runner("report", "categories")
        print(out, err)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        mine = [r for r in rows[1:-1] if r[0] == cat][0]
        return int(mine[2]), Decimal(mine[3]), Decimal(rows[-1][3])

    count_before, inflow_before, total_before = snapshot()
    new_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(txn_id=new_id, date="2099-03-11", account="ZZRCS1", category=cat, amount=delta, memo="rcs")
    count_after, inflow_after, total_after = snapshot()
    assert count_after == count_before + 1
    assert inflow_after - inflow_before == Decimal(delta) / 100
    assert total_after - total_before == Decimal(delta) / 100
=== END AC categories-computed-from-storage ===

=== AC categories-usage ===
Intent: Extra arguments to the categories report exit 2 with empty stdout.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "categories", "extra")
print(code, out, err)
assert code == 2
assert out == ""
assert err.strip() != ""
=== END AC categories-usage ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query at run time; no row, count or total is hardcoded.
- Unused categories always appear.
- Money is integer cents; no floating point at any layer.
- The report never writes to the database.
