# FEATURE: Report Balances

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | The `ledger report balances` command that reports each account's transaction count and balance computed from stored data. |
| Depends On | FEATURE-LoadTransactions.md, FEATURE-Transfer.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger report balances |
| Consumes | ledger.register_command, persistence.open_database, csv_output.write_rows, csv_output.format_cents |

## Purpose

`ledger report balances` writes one row per account with its transaction count and balance, then a total row. Every value is computed from stored transactions in integer cents.

## Behavior

- Header: `account,name,transactions,balance`.
- One row per account ordered by code in byte order (digits before letters), including accounts with no transactions (count 0, balance 0.00).
- `balance` is the sum of the account's transaction amounts in integer cents, formatted with exactly two decimals and a leading `-` when negative.
- Final row: `TOTAL,,<count>,<sum>` where `<count>` is the total number of transactions and `<sum>` the sum of all balances. A zero total is `0.00`, never `-0.00`.
- On an empty ledger the output is the header and `TOTAL,,0,0.00`.
- No value is embedded; everything is derived from `accounts.list` and `transactions.list`.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC report-balances-seeded ===
Intent: Balances over the loaded seed data match values derived from the seed files, including an unused account sorted first.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

with open("sources/seed_accounts.csv", newline="") as fh:
    accounts = {r["account"]: r["name"] for r in csv.DictReader(fh)}
with open("sources/seed_transactions.csv", newline="") as fh:
    txns = list(csv.DictReader(fh))

extra_code, extra_name = "0EMPTY", "Unused Account"

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    print(out, err)
    assert code == 0

with db_session() as db:
    db.accounts.create(account=extra_code, name=extra_name)
accounts[extra_code] = extra_name

counts = {c: 0 for c in accounts}
sums = {c: 0 for c in accounts}
for t in txns:
    counts[t["account"]] += 1
    sums[t["account"]] += int(Decimal(t["amount"]) * 100)

code, out, err = cli_runner("report", "balances")
print(out, err)
assert code == 0
assert "\r" not in out and out.endswith("\n")
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
codes = sorted(accounts)
assert [r[0] for r in rows[1:-1]] == codes
assert codes[0] == extra_code
for r in rows[1:-1]:
    assert r[1] == accounts[r[0]]
    assert int(r[2]) == counts[r[0]]
    assert re.fullmatch(r"-?\d+\.\d\d", r[3])
    assert Decimal(r[3]) * 100 == sums[r[0]]
total = rows[-1]
assert total[0] == "TOTAL" and total[1] == ""
assert int(total[2]) == len(txns)
assert re.fullmatch(r"-?\d+\.\d\d", total[3])
assert Decimal(total[3]) * 100 == sum(sums.values())
=== END AC report-balances-seeded ===

=== AC report-balances-empty ===
Intent: On an empty ledger the report writes its header and a zero total row.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner

code, out, err = cli_runner("init")
assert code == 0
code, out, err = cli_runner("report", "balances")
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["account", "name", "transactions", "balance"]
assert len(rows) == 2
assert rows[1][0] == "TOTAL" and rows[1][1] == ""
assert int(rows[1][2]) == 0
assert re.fullmatch(r"0\.00", rows[1][3])
assert Decimal(rows[1][3]) == 0
=== END AC report-balances-empty ===

=== AC report-balances-after-transfer ===
Intent: Balances are recomputed from stored rows after a transfer, moving cash between two accounts and keeping the total.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner

src, dst = "DRAWER1", "SAFE"
amount = "500.00"

for args in (
    ("init",),
    ("load", "accounts", "sources/seed_accounts.csv"),
    ("load", "categories", "sources/seed_categories.csv"),
    ("load", "transactions", "sources/seed_transactions.csv"),
):
    code, out, err = cli_runner(*args)
    assert code == 0

def balances():
    code, out, err = cli_runner("report", "balances")
    print(out, err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return {r[0]: (int(r[2]), Decimal(r[3])) for r in rows[1:]}

before = balances()
code, out, err = cli_runner("transfer", src, dst, amount, "2026-04-03")
print(out, err)
assert code == 0
after = balances()
assert after[src][0] == before[src][0] + 1
assert after[dst][0] == before[dst][0] + 1
assert after[src][1] == before[src][1] - Decimal(amount)
assert after[dst][1] == before[dst][1] + Decimal(amount)
assert after["TOTAL"][1] == before["TOTAL"][1]
assert after["TOTAL"][0] == before["TOTAL"][0] + 2
=== END AC report-balances-after-transfer ===

## User Acceptance

- None.

## Guardrails

- Every value is computed from stored data; no count, balance or total is embedded.
- Money is integer cents; no floating point at any layer.
- A zero total is written `0.00`, never `-0.00`.
