# FEATURE: Count

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implement `ledger count`, which prints the row count of each table. |
| Depends On | FEATURE-DatabaseSelection.md, FEATURE-CsvOutput.md, DATABASE.md |
| Provides | ledger count |
| Consumes | ledgerlib.config, ledgerlib.csvout |

## Purpose

`ledger count` prints `table,rows` and then one row each for `accounts`, `categories` and `transactions`, in that order. Each count is taken from the stored rows at run time.

## Behavior

- `cli/commands/count.py` exposes `run(args) -> list[str]`.
- Any argument is a usage error (exit 2).
- A missing table or unreachable database exits 1 with nothing on standard output.
- Counts are `len` of the declared list operations; none is hardcoded or cached.

## Database Interface


- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC count-rows ===
Intent: Count prints the header and the three tables in order with counts equal to the stored rows read back through the persistence interface.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

acct = "ZZCNT1"
cat = "ZZCNTCAT1"
with db_session() as db:
    db.accounts.create(account=acct, name="Count Acct")
    db.categories.create(category=cat, description="Count Cat")
    db.transactions.create(txn_id=961001, date="2026-05-01", account=acct, category=cat, amount=100, memo="c")
    db.transactions.create(txn_id=961002, date="2026-05-02", account=acct, category=cat, amount=200, memo="c")

    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 0
    assert out.endswith("\n")
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["table", "rows"]
    assert [r[0] for r in rows[1:]] == ["accounts", "categories", "transactions"]
    assert len(rows) == 4
    assert int(rows[1][1]) == len(db.accounts.list())
    assert int(rows[2][1]) == len(db.categories.list())
    assert int(rows[3][1]) == len(db.transactions.list())
=== END AC count-rows ===

=== AC count-tracks-changes ===
Intent: Count reflects an added account by exactly one row compared with a count read before the change.

import csv
import io
from persistence.testing import db_session
from cli.testing import cli_runner

def accounts_count():
    code, out, err = cli_runner("count")
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    return int(rows[1][1])

with db_session() as db:
    before = accounts_count()
    db.accounts.create(account="ZZCNT2", name="Count Two")
    after = accounts_count()
    assert after == before + 1
=== END AC count-tracks-changes ===

=== AC count-usage ===
Intent: Count with an extra argument is a usage error with exit 2 and empty standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("count", "extra")
assert code == 2
assert out == ""
assert err != ""
=== END AC count-usage ===

## User Acceptance

- None.

## Guardrails

- No count is hardcoded; every value is computed from stored rows.
- Standard output holds only the CSV table on success.
