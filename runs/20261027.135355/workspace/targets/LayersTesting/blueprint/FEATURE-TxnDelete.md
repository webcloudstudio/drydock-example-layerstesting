# FEATURE: Transaction Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn delete <id>`, which removes a transaction unless its account balance would go below zero. |
| Depends On | FEATURE-TxnPost.md, FEATURE-BalanceRule.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn delete |
| Consumes | ledger_core.transactions, ledger_core.balances, cli.registry |

## Purpose

Delete one transaction by id. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

## Behavior

1. Argument count other than one after `txn delete` exits 2.
2. A non-integer id exits 3.
3. An absent id exits 4.
4. The account's balance after removal is the stored balance minus the transaction's amount, in integer cents through `ledger_core.balances`. A negative result exits 3 and the row is kept.
5. Otherwise the row is deleted and the command prints two lines: `deleted` and the id.
6. A failing command writes nothing to standard output and one diagnostic line to standard error.

## Database Interface

- None — persistence is owned by DATABASE.md and reached through `ledger_core.transactions`.

## Programmatic Acceptance

=== AC txn-delete-success ===
Intent: Deleting an existing transaction exits 0, prints `deleted` then the id, and a separate read finds no row.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

acct, cat, tid = "ZZDL1", "ZZDLC1", 900200001
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=tid, date="2026-05-01", account=acct, category=cat, amount=-500, memo="")
    db.transactions.create(txn_id=tid + 1, date="2026-05-01", account=acct, category=cat, amount=9000, memo="")
    code, out, err = cli_runner("txn", "delete", str(tid))
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[1] == [str(tid)]
    assert rows[0] == ["deleted"]
    assert db.transactions.get(txn_id=tid) is None
    assert db.transactions.get(txn_id=tid + 1) is not None
=== END AC txn-delete-success ===

=== AC txn-delete-absent ===
Intent: Deleting an id that does not exist exits 4 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

tid = 900299999
with db_session() as db:
    assert db.transactions.get(txn_id=tid) is None
    code, out, err = cli_runner("txn", "delete", str(tid))
    print(out)
    print(err)
    assert code == 4
    assert out == ""
=== END AC txn-delete-absent ===

=== AC txn-delete-negative-balance ===
Intent: Deleting a +10000 deposit while a -4000 payment remains would leave -4000, so exit 3 and the row stays; deleting the payment instead leaves a positive balance and succeeds.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZDL2", "ZZDLC2"
tid_in, tid_out = 900200002, 900200003
amount_in = 10000
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Account")
    db.categories.create(category=cat, description="Delete Category")
    db.transactions.create(txn_id=tid_in, date="2026-05-02", account=acct, category=cat, amount=amount_in, memo="")
    db.transactions.create(txn_id=tid_out, date="2026-05-02", account=acct, category=cat, amount=-4000, memo="")
    code, out, err = cli_runner("txn", "delete", str(tid_in))
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    kept = db.transactions.get(txn_id=tid_in)
    assert kept is not None
    assert f(kept, "amount") == amount_in
    code, out, err = cli_runner("txn", "delete", str(tid_out))
    print(out)
    print(err)
    assert code == 0
    assert db.transactions.get(txn_id=tid_out) is None
=== END AC txn-delete-negative-balance ===

=== AC txn-delete-bad-id ===
Intent: A non-integer id is rejected with exit 3 and nothing on stdout.

from cli.testing import cli_runner

code, out, err = cli_runner("txn", "delete", "abc")
print(out)
print(err)
assert code == 3
assert out == ""
=== END AC txn-delete-bad-id ===

=== AC txn-delete-usage ===
Intent: A wrong argument count for txn delete exits 2 with nothing on stdout.

from cli.testing import cli_runner

for args in [("txn", "delete"), ("txn", "delete", "1", "2")]:
    code, out, err = cli_runner(*args)
    print(out)
    print(err)
    assert code == 2
    assert out == ""
=== END AC txn-delete-usage ===

## User Acceptance

- None.

## Guardrails

- The balance check runs before the delete, so a rejected delete writes nothing.
- Standard output stays empty on any failure; the diagnostic goes to standard error.
- Amounts are integer cents; floating point is never used for money.
