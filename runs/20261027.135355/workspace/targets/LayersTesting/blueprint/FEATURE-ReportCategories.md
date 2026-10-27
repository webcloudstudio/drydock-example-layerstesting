# FEATURE: Report Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report categories`, per-category transaction count, inflow, outflow, and net with a total row, computed from stored data. |
| Depends On | FEATURE-CliEntry.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger report categories |
| Consumes | ledger_core.money, cli.registry |

## Purpose

Report totals by category, including categories with no transactions. Every value is computed from queries over stored rows. Persistence is reached only through the generated `persistence` package via `ledger_core`.

## Behavior

1. Header `category,description,transactions,inflow,outflow,net`.
2. One row per category ordered by category code, including categories with no transactions (count 0 and zero amounts).
3. `inflow` is the sum of positive amounts, `outflow` the sum of the absolute values of negative amounts written as a positive number, and `net` is inflow minus outflow.
4. A final row `TOTAL,,<count>,<inflow>,<outflow>,<net>` over all transactions.
5. Amounts use exactly two decimals, a leading `-` when negative, and no thousands separator.
6. Extra arguments exit 2. Output uses `\n` endings, no quoting, and no trailing spaces.

## Database Interface

- None — persistence is owned by DATABASE.md and reached through `ledger_core`.

## Programmatic Acceptance

=== AC report-categories-values ===
Intent: Each category row and the TOTAL row match inflow, outflow, net, and count derived from stored transactions, including a category with mixed signs and an empty category.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

def fmt(c):
    sign = "-" if c < 0 else ""
    q, r = divmod(abs(c), 100)
    return f"{sign}{q}.{r:02d}"

def summarize(amounts):
    inflow = sum(a for a in amounts if a > 0)
    outflow = sum(-a for a in amounts if a < 0)
    return [str(len(amounts)), fmt(inflow), fmt(outflow), fmt(inflow - outflow)]

acct, mixed, empty = "ZZRC1", "ZZRCM", "ZZRCE"
with db_session() as db:
    db.accounts.create(account=acct, name="Category Account")
    db.categories.create(category=mixed, description="Mixed Category")
    db.categories.create(category=empty, description="Empty Category")
    db.transactions.create(txn_id=900500001, date="2026-05-01", account=acct, category=mixed, amount=100050, memo="")
    db.transactions.create(txn_id=900500002, date="2026-05-02", account=acct, category=mixed, amount=-2505, memo="")
    db.transactions.create(txn_id=900500003, date="2026-05-03", account=acct, category=mixed, amount=-7, memo="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["category", "description", "transactions", "inflow", "outflow", "net"]
    txns = db.transactions.list()
    expected = []
    for cat in sorted(db.categories.list(), key=lambda r: f(r, "category")):
        amounts = [f(t, "amount") for t in txns if f(t, "category") == f(cat, "category")]
        expected.append([f(cat, "category"), f(cat, "description")] + summarize(amounts))
    expected.append(["TOTAL", ""] + summarize([f(t, "amount") for t in txns]))
    assert rows[1:] == expected
=== END AC report-categories-values ===

=== AC report-categories-empty ===
Intent: A category with no transactions is listed with count 0 and zero inflow, outflow, and net.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def fmt(c):
    sign = "-" if c < 0 else ""
    q, r = divmod(abs(c), 100)
    return f"{sign}{q}.{r:02d}"

empty = "ZZRCE2"
with db_session() as db:
    db.categories.create(category=empty, description="Nothing here")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    row = [r for r in rows[1:-1] if r[0] == empty][0]
    assert row[2:] == ["0", fmt(0), fmt(0), fmt(0)]
=== END AC report-categories-empty ===

=== AC report-categories-order ===
Intent: Categories are ordered by code regardless of creation order, and the TOTAL row is last.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

codes = ["ZZRCB", "ZZRCA"]
with db_session() as db:
    for c in codes:
        db.categories.create(category=c, description="Order " + c)
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    seen = [r[0] for r in rows[1:-1]]
    assert seen == sorted(seen)
    assert rows[-1][0] == "TOTAL"
=== END AC report-categories-order ===

=== AC report-categories-net-identity ===
Intent: For every row including TOTAL, net equals inflow minus outflow, and outflow is never written with a leading minus.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def cents(text):
    neg = text.startswith("-")
    whole, frac = text.lstrip("-").split(".")
    v = int(whole) * 100 + int(frac)
    return -v if neg else v

acct, cat = "ZZRC2", "ZZRCN"
with db_session() as db:
    db.accounts.create(account=acct, name="Net Account")
    db.categories.create(category=cat, description="Net Category")
    db.transactions.create(txn_id=900500010, date="2026-05-01", account=acct, category=cat, amount=1000, memo="")
    db.transactions.create(txn_id=900500011, date="2026-05-02", account=acct, category=cat, amount=-1500, memo="")
    code, out, err = cli_runner("report", "categories")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))[1:]
    for r in rows:
        assert not r[4].startswith("-")
        assert cents(r[5]) == cents(r[3]) - cents(r[4])
=== END AC report-categories-net-identity ===

=== AC report-categories-format ===
Intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "categories")
print(out)
print(err)
assert code == 0
assert out.endswith("\n")
assert "\r" not in out
assert all(line == line.rstrip(" ") for line in out.split("\n"))
=== END AC report-categories-format ===

=== AC report-categories-usage ===
Intent: Extra arguments exit 2 with nothing on stdout.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "categories", "extra")
print(out)
print(err)
assert code == 2
assert out == ""
=== END AC report-categories-usage ===

## User Acceptance

- None.

## Guardrails

- No report row, count, or total is hardcoded; every value comes from a query.
- Money is integer cents until formatting; floating point is never used.
- The command writes nothing to the database.
