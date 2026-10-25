# FEATURE: Account Get

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Implements `ledger account get <code>`, printing one account row with its transaction count and balance. |
| Depends On | FEATURE-AccountAdd.md, FEATURE-CliEntry.md, FEATURE-LedgerCore.md, DATABASE.md |
| Provides | ledger account get |
| Consumes | accounts.get, transactions.list |

## Purpose

Read one account by code and print it as CSV. The transaction count and balance are computed from the
database on every call and are never stored.

## Command Contract

| Aspect | Rule |
|--------|------|
| Invocation | `ledger account get <code>` with exactly one argument. |
| Success stdout | Header `account,name,transactions,balance`, then one row: code, name, count of the account's transactions, balance as two-decimal text. |
| Balance | Sum of the account's integer-cent amounts, formatted with exactly two decimals, a leading `-` when negative, no thousands separator. No floating point. |
| Absent account | Exit 4, nothing on stdout, one diagnostic line on stderr. |
| Wrong argument count | Exit 2, nothing on stdout. |
| Writes | None. |

## Database Interface

- `FEATURE-ACCOUNT-001` — read: retrieve an account by code - supplies: `account` - returns: `account`, `name`
- `FEATURE-TXN-002` — read: list the account's transactions to count and sum them - supplies: `account` - returns: `amount`

## Programmatic Acceptance

=== AC account-get-empty ===
Intent: Getting an account with no transactions prints its row with a zero count and a zero balance.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "AGETE1"
    name = "Get Empty"
    db.accounts.create(account=code, name=name)
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["account", "name", "transactions", "balance"]
    assert len(rows) == 2
    assert rows[1][0] == code
    assert rows[1][1] == name
    assert int(rows[1][2]) == 0
    assert int(rows[1][3].replace(".", "")) == 0
    assert len(rows[1][3].split(".")[1]) == 2
=== END AC account-get-empty ===

=== AC account-get-balance ===
Intent: Getting an account computes its transaction count and balance from stored integer cents.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "AGETB1"
    cat = "AGETBC1"
    name = "Get Balance"
    db.accounts.create(account=code, name=name)
    db.categories.create(category=cat, description="Get Balance Cat")
    amounts = [5000, -1234]
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    for offset, cents in enumerate(amounts):
        db.transactions.create(
            txn_id=base + offset, date="2026-05-01", account=code,
            category=cat, amount=cents, memo="",
        )
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    print(err)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][0] == code
    assert rows[1][1] == name
    assert int(rows[1][2]) == len(amounts)
    assert int(rows[1][3].replace(".", "")) == sum(amounts)
    assert len(rows[1][3].split(".")[1]) == 2
=== END AC account-get-balance ===

=== AC account-get-negative-format ===
Intent: A balance is never printed negative because the ledger forbids it, and a positive one has no thousands separator.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    code = "AGETF1"
    cat = "AGETFC1"
    db.accounts.create(account=code, name="Get Format")
    db.categories.create(category=cat, description="Get Format Cat")
    cents = 123456789
    base = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=base, date="2026-05-01", account=code,
        category=cat, amount=cents, memo="",
    )
    rc, out, err = cli_runner("account", "get", code)
    print(out)
    assert rc == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert "," not in rows[1][3]
    assert int(rows[1][3].replace(".", "")) == cents
=== END AC account-get-negative-format ===

=== AC account-get-absent ===
Intent: Getting an absent account exits 4 and writes nothing to stdout.

from persistence.testing import db_session
from cli.testing import cli_runner

with db_session() as db:
    absent = "AGETNO1"
    assert db.accounts.get(account=absent) is None
    rc, out, err = cli_runner("account", "get", absent)
    print(err)
    assert rc == 4
    assert out == ""
=== END AC account-get-absent ===

=== AC account-get-usage ===
Intent: Getting an account with a wrong argument count exits 2 and writes nothing to stdout.

from cli.testing import cli_runner

rc, out, err = cli_runner("account", "get")
assert rc == 2
assert out == ""
rc, out, err = cli_runner("account", "get", "ONE", "TWO")
assert rc == 2
assert out == ""
=== END AC account-get-usage ===

## User Acceptance

- None.

## Guardrails

- The count and balance are computed from the database on every call; no value is hard-coded or stored.
- Amounts are integer cents internally and never pass through floating point.
- The command performs no write.
- Nothing is written to stdout on failure.
