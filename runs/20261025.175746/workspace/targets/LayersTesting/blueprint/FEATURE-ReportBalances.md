# FEATURE: Report Balances

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Implements `ledger report balances`, the per-account transaction count and balance with a TOTAL row. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-CliFoundation.md, FEATURE-BalanceRules.md |
| Provides    | ledger report balances |
| Consumes    | accounts.list, transactions.list, account_summary |

## Purpose

Report each account's transaction count and balance, computed from stored rows in integer cents.

## Trigger

`./ledger report balances`

## Sequence

1. List accounts through `accounts.list` (ordered by code).
2. For each account compute the transaction count and the balance (sum of amounts, in cents) from
   `transactions.list` via `account_summary`.
3. Print the header `account,name,transactions,balance`, one row per account ordered by code, then
   `TOTAL,,<count>,<sum>` where count and sum cover every account.
4. Amounts print with exactly two decimal places, a leading `-` when negative, and no thousands separator.
5. Any argument beyond `balances` is a usage error (exit 2).

## Reads

- `accounts.list`, `transactions.list`.

## Writes

- None.

## Database Interface

- `FEATURE-ACCOUNTS-003` — read: list accounts in code order - supplies: `account` - returns: `account`, `name`
- `FEATURE-TRANSACTIONS-003` — read: list transactions for an account - supplies: `account` - returns: `txn_id`, `account`, `amount`

## Programmatic Acceptance

=== AC report-balances-rows ===
Intent: The report shows each created account's transaction count and balance in two-decimal form, with zero for an account without transactions.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

funded = "UTRB1"
empty = "UTRB2"
cat = "UTRBC"
amounts = [100000, -30050, 1999]
expected_balance = sum(amounts)
with db_session() as db:
    db.accounts.create(account=funded, name="Funded")
    db.accounts.create(account=empty, name="Empty")
    db.categories.create(category=cat, description="Bal")
    for offset, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=920001 + offset, date="2026-05-01", account=funded,
            category=cat, amount=cents, memo="",
        )
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    by_code = {r[0]: r for r in rows[1:]}
    assert by_code[funded][1] == "Funded"
    assert int(by_code[funded][2]) == len(amounts)
    assert to_cents(by_code[funded][3]) == expected_balance
    assert by_code[empty][1] == "Empty"
    assert int(by_code[empty][2]) == 0
    assert to_cents(by_code[empty][3]) == 0
=== END AC report-balances-rows ===

=== AC report-balances-order-and-total ===
Intent: Account rows are ordered by code and the TOTAL row equals the sum of the account rows' counts and balances.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

late = "UTRC9"
early = "UTRC1"
cat = "UTRCC"
with db_session() as db:
    db.accounts.create(account=late, name="Late")
    db.accounts.create(account=early, name="Early")
    db.categories.create(category=cat, description="Bal")
    db.transactions.create(
        txn_id=920101, date="2026-05-01", account=late, category=cat, amount=2500, memo=""
    )
    db.transactions.create(
        txn_id=920102, date="2026-05-01", account=early, category=cat, amount=700, memo=""
    )
    code, out, err = cli_runner("report", "balances")
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    data = rows[1:-1]
    codes = [r[0] for r in data]
    assert codes == sorted(codes)
    assert codes.index(early) < codes.index(late)
    total = rows[-1]
    assert total[0] == "TOTAL"
    assert total[1] == ""
    assert int(total[2]) == sum(int(r[2]) for r in data)
    assert to_cents(total[3]) == sum(to_cents(r[3]) for r in data)
    stored_count = len(db.transactions.list())
    assert int(total[2]) == stored_count
=== END AC report-balances-order-and-total ===

=== AC report-balances-reflects-changes ===
Intent: The report is recomputed from stored rows, so a later transaction changes the balance by exactly its amount.

import csv
import io
import re
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

def to_cents(text):
    assert re.fullmatch(r"-?\d+\.\d{2}", text)
    return int(Decimal(text) * 100)

def balance_of(out, account):
    rows = list(csv.reader(io.StringIO(out)))
    return {r[0]: r for r in rows[1:]}[account]

acct = "UTRD1"
cat = "UTRDC"
first = 8000
second = 1234
with db_session() as db:
    db.accounts.create(account=acct, name="Moves")
    db.categories.create(category=cat, description="Bal")
    db.transactions.create(
        txn_id=920201, date="2026-05-01", account=acct, category=cat, amount=first, memo=""
    )
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    before = to_cents(balance_of(out, acct)[3])
    assert before == first
    db.transactions.create(
        txn_id=920202, date="2026-05-02", account=acct, category=cat, amount=second, memo=""
    )
    code, out, err = cli_runner("report", "balances")
    assert code == 0
    row = balance_of(out, acct)
    assert to_cents(row[3]) == before + second
    assert int(row[2]) == 2
=== END AC report-balances-reflects-changes ===

=== AC report-balances-usage ===
Intent: An extra argument after balances and an unknown report each exit 2 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session():
    code, out, err = cli_runner("report", "balances", "extra")
    assert code == 2 and out == ""
    code, out, err = cli_runner("report", "nosuchreport")
    assert code == 2 and out == ""
    code, out, err = cli_runner("report")
    assert code == 2 and out == ""
=== END AC report-balances-usage ===

## User Acceptance

- None.

## Guardrails

- Every value comes from a query of stored rows; no row, count, or total is hardcoded or stored.
- Money is integer cents internally; no floating point at any layer.
- The command writes nothing to the database.
- Diagnostics go to standard error only.
