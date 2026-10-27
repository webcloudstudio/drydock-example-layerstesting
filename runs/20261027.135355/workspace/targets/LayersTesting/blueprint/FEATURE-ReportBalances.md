# FEATURE: Report Balances

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger report balances`, a per-account count and balance report with a total row, computed from stored data. |
| Depends On | FEATURE-CliEntry.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger report balances |
| Consumes | ledger_core.money, cli.registry |

## Purpose

Report each account's transaction count and balance. Every value is computed from queries over stored rows; none is embedded. Persistence is reached only through the generated `persistence` package via `ledger_core`.

## Behavior

1. Header `account,name,transactions,balance`.
2. One row per account ordered by account code; accounts without transactions appear with count 0 and balance `0.00`.
3. A final row `TOTAL,,<count>,<sum>` where count is the number of all transactions and sum is the sum of all amounts.
4. Balances are integer-cent sums formatted with exactly two decimals, a leading `-` when negative, and no thousands separator.
5. Extra arguments exit 2. Output uses `\n` endings, no quoting, and no trailing spaces.

## Database Interface

- None — persistence is owned by DATABASE.md and reached through `ledger_core`.

## Programmatic Acceptance

=== AC report-balances-values ===
Intent: Each account row carries the count and formatted balance derived from stored transactions, and the TOTAL row carries the overall count and sum; expectations are computed from the stored rows.

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

a1, a2, cat = "ZZRB1", "ZZRB2", "ZZRBC1"
with db_session() as db:
    db.accounts.create(account=a1, name="Report One")
    db.accounts.create(account=a2, name="Report Two")
    db.categories.create(category=cat, description="Report Category")
    db.transactions.create(txn_id=900400001, date="2026-05-01", account=a1, category=cat, amount=123456, memo="")
    db.transactions.create(txn_id=900400002, date="2026-05-02", account=a1, category=cat, amount=-2345, memo="")
    db.transactions.create(txn_id=900400003, date="2026-05-03", account=a2, category=cat, amount=5, memo="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    txns = db.transactions.list()
    expected = []
    for acc in sorted(db.accounts.list(), key=lambda r: f(r, "account")):
        mine = [f(t, "amount") for t in txns if f(t, "account") == f(acc, "account")]
        expected.append([f(acc, "account"), f(acc, "name"), str(len(mine)), fmt(sum(mine))])
    expected.append(["TOTAL", "", str(len(txns)), fmt(sum(f(t, "amount") for t in txns))])
    assert rows[1:] == expected
=== END AC report-balances-values ===

=== AC report-balances-order-and-empty ===
Intent: Accounts are ordered by code regardless of creation order, and an account with no transactions still appears with count 0 and a zero balance.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def fmt(c):
    sign = "-" if c < 0 else ""
    q, r = divmod(abs(c), 100)
    return f"{sign}{q}.{r:02d}"

codes = ["ZZRB4", "ZZRB3"]
with db_session() as db:
    for c in codes:
        db.accounts.create(account=c, name="Empty " + c)
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))[1:-1]
    seen = [r[0] for r in rows]
    assert seen == sorted(seen)
    for c in codes:
        row = [r for r in rows if r[0] == c][0]
        assert row[2] == "0"
        assert row[3] == fmt(0)
=== END AC report-balances-order-and-empty ===

=== AC report-balances-total-consistency ===
Intent: The TOTAL row equals the sum of the per-account rows, including negative-free cent arithmetic across accounts.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def cents(text):
    neg = text.startswith("-")
    whole, frac = text.lstrip("-").split(".")
    v = int(whole) * 100 + int(frac)
    return -v if neg else v

a1, a2, cat = "ZZRB5", "ZZRB6", "ZZRBC2"
with db_session() as db:
    db.accounts.create(account=a1, name="Total One")
    db.accounts.create(account=a2, name="Total Two")
    db.categories.create(category=cat, description="Report Category")
    db.transactions.create(txn_id=900400010, date="2026-05-01", account=a1, category=cat, amount=70001, memo="")
    db.transactions.create(txn_id=900400011, date="2026-05-01", account=a2, category=cat, amount=30002, memo="")
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    body, total = rows[1:-1], rows[-1]
    assert total[0] == "TOTAL" and total[1] == ""
    assert int(total[2]) == sum(int(r[2]) for r in body)
    assert cents(total[3]) == sum(cents(r[3]) for r in body)
=== END AC report-balances-total-consistency ===

=== AC report-balances-format ===
Intent: Output uses newline endings only, ends with a newline, and no line carries trailing spaces.

from cli.testing import cli_runner

code, out, err = cli_runner("report", "balances")
print(out)
print(err)
assert code == 0
assert out.endswith("\n")
assert "\r" not in out
assert all(line == line.rstrip(" ") for line in out.split("\n"))
=== END AC report-balances-format ===

=== AC report-balances-usage ===
Intent: Extra arguments and an unknown report name exit 2 with nothing on stdout.

from cli.testing import cli_runner

for args in [("report", "balances", "extra"), ("report", "nosuchreport"), ("report",)]:
    code, out, err = cli_runner(*args)
    print(out)
    print(err)
    assert code == 2
    assert out == ""
=== END AC report-balances-usage ===

## User Acceptance

- None.

## Guardrails

- No report row, count, or total is hardcoded; every value comes from a query.
- Money is integer cents until formatting; floating point is never used.
- The command writes nothing to the database.
