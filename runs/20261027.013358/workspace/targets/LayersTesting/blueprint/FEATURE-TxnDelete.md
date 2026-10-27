# FEATURE: Transaction Delete

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn delete <id>` removing one transaction under the non-negative balance rule. |
| Depends On | FEATURE-TxnGet.md, DATABASE.md |
| Provides | ledger txn delete |
| Consumes | ledger txn get |

## Purpose

Remove one stored transaction through the `txn` verb table in `cli/commands/txn.py`.

## Behavior

1. Usage: `ledger txn delete <id>`; any other argument count is a usage error (exit 2).
2. An id that is not decimal digits exits 3. An absent id exits 4.
3. If removing the transaction would leave the account balance below zero, exit 3 and change nothing.
4. Otherwise delete the row and print `deleted` then the id.
5. Deleting one leg of a transfer is permitted under the same rule; the paired leg is left unchanged.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC txn-delete-success ===
Intent: Deleting a transaction prints deleted and the id, and a separate read finds it gone.

import csv
import io
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTDEL1"
cat = "ZZTDCAT1"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete One")
    db.categories.create(category=cat, description="Delete Cat")
    txn_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=450, memo="gone"
    )
    exit_code, out, err = cli_runner("txn", "delete", str(txn_id))
    print(out)
    print(err)
    assert exit_code == 0
    assert list(csv.reader(io.StringIO(out))) == [["deleted"], [str(txn_id)]]
    assert db.transactions.get(txn_id=txn_id) is None
=== END AC txn-delete-success ===

=== AC txn-delete-rejects-negative-balance ===
Intent: Deleting an inflow that funds a later outflow would leave a negative balance, so it exits 3 and both rows remain.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZZTDEL2"
cat = "ZZTDCAT2"
with db_session() as db:
    db.accounts.create(account=acct, name="Delete Two")
    db.categories.create(category=cat, description="Delete Cat Two")
    inflow_id = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    outflow_id = inflow_id + 1
    db.transactions.create(
        txn_id=inflow_id, date="2026-04-01", account=acct, category=cat, amount=1000, memo="in"
    )
    db.transactions.create(
        txn_id=outflow_id, date="2026-04-02", account=acct, category=cat, amount=-500, memo="out"
    )
    exit_code, out, err = cli_runner("txn", "delete", str(inflow_id))
    print(out, err)
    assert exit_code == 3
    assert out == ""
    assert db.transactions.get(txn_id=inflow_id) is not None
    assert db.transactions.get(txn_id=outflow_id) is not None
=== END AC txn-delete-rejects-negative-balance ===

=== AC txn-delete-transfer-leg ===
Intent: Deleting one leg of a transfer is allowed when the balance rule holds, and the paired leg is left unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

src = "ZZTDEL3A"
dst = "ZZTDEL3B"
cat = "ZZTDCAT3"
with db_session() as db:
    db.accounts.create(account=src, name="Leg Source")
    db.accounts.create(account=dst, name="Leg Dest")
    db.categories.create(category=cat, description="Leg Cat")
    base = max([r.txn_id for r in db.transactions.list()], default=0) + 1
    seed_id, out_id, in_id = base, base + 1, base + 2
    db.transactions.create(
        txn_id=seed_id, date="2026-04-01", account=src, category=cat, amount=1000, memo="seed"
    )
    db.transactions.create(
        txn_id=out_id, date="2026-04-02", account=src, category=cat, amount=-300, memo="leg out"
    )
    db.transactions.create(
        txn_id=in_id, date="2026-04-02", account=dst, category=cat, amount=300, memo="leg in"
    )
    exit_code, out, err = cli_runner("txn", "delete", str(in_id))
    print(out, err)
    assert exit_code == 0
    assert db.transactions.get(txn_id=in_id) is None
    paired = db.transactions.get(txn_id=out_id)
    assert paired is not None
    assert paired.amount == -300
    assert paired.account == src
=== END AC txn-delete-transfer-leg ===

=== AC txn-delete-absent ===
Intent: Deleting an id no transaction holds exits 4 with nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    missing = max([r.txn_id for r in db.transactions.list()], default=0) + 1000
    exit_code, out, err = cli_runner("txn", "delete", str(missing))
    print(out)
    print(err)
    assert exit_code == 4
    assert out == ""
=== END AC txn-delete-absent ===

=== AC txn-delete-bad-input ===
Intent: A non-digit id exits 3 and a missing id is a usage error with exit 2.

from cli.testing import cli_runner

code_bad, out_bad, err_bad = cli_runner("txn", "delete", "abc")
print(out_bad, err_bad)
assert code_bad == 3
assert out_bad == ""
code_usage, out_usage, err_usage = cli_runner("txn", "delete")
print(out_usage, err_usage)
assert code_usage == 2
assert out_usage == ""
=== END AC txn-delete-bad-input ===

## User Acceptance

- None.

## Guardrails

- The balance check completes before the delete; a rejected delete changes nothing.
- Deleting a transfer leg never alters the paired leg.
- Diagnostics go to standard error only.
