# FEATURE: Transaction Amend

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger txn amend <id> <amount>`, which changes only a transaction's amount without leaving any account balance below zero. |
| Depends On | FEATURE-TxnPost.md, FEATURE-Validation.md, FEATURE-BalanceRule.md, FEATURE-CliEntry.md, DATABASE.md |
| Provides | ledger txn amend |
| Consumes | ledger_core.transactions, ledger_core.validation, ledger_core.balances, cli.registry |

## Purpose

Amend the amount of an existing transaction. Only the amount changes; date, account, category, and memo are untouched. Persistence is reached only through `ledger_core.transactions`, which calls the generated `persistence` package.

## Behavior

1. Argument count other than two after `txn amend` exits 2.
2. The id must be an integer; otherwise exit 3.
3. The amount is validated with `ledger_core.validation` (`-?DIGITS[.D[D]]`, at most two decimals, never zero); a violation exits 3.
4. An absent id exits 4.
5. The resulting balance of the transaction's account is the stored balance minus the old amount plus the new amount, computed in integer cents through `ledger_core.balances`. A negative result exits 3 and nothing is written.
6. Otherwise only the amount is updated and the updated row is printed as `txn_id,date,account,category,amount,memo` with a two-decimal amount.
7. A failing command writes nothing to standard output and one diagnostic line to standard error.

## Database Interface

- None — persistence is owned by DATABASE.md and reached through `ledger_core.transactions`.

## Programmatic Acceptance

=== AC txn-amend-success ===
Intent: Amending an existing transaction exits 0, prints the updated row with the supplied amount text, and a separate read shows the new integer cents.

from cli.testing import cli_runner
from persistence.testing import db_session
import csv
import io

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat, tid = "ZZAM1", "ZZAMC1", 900100001
day = "2026-05-01"
newtext = "50.00"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=10000, memo="amend probe")
    code, out, err = cli_runner("txn", "amend", str(tid), newtext)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[1][0] == str(tid)
    assert rows[1][1] == day
    assert rows[1][4] == newtext
    assert f(db.transactions.get(txn_id=tid), "amount") == int(newtext.replace(".", ""))
=== END AC txn-amend-success ===

=== AC txn-amend-only-amount ===
Intent: Amend changes only the amount; date, account, category, and memo read back exactly as they were created.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat, tid = "ZZAM2", "ZZAMC2", 900100002
day = "2026-05-02"
note = "keep this memo"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=tid, date=day, account=acct, category=cat, amount=2000, memo=note)
    code, out, err = cli_runner("txn", "amend", str(tid), "35.50")
    print(out)
    print(err)
    assert code == 0
    back = db.transactions.get(txn_id=tid)
    assert f(back, "date") == day
    assert f(back, "account") == acct
    assert f(back, "category") == cat
    assert f(back, "memo") == note
=== END AC txn-amend-only-amount ===

=== AC txn-amend-absent ===
Intent: Amending an id that does not exist exits 4, prints nothing to stdout, and creates no row.

from cli.testing import cli_runner
from persistence.testing import db_session

tid = 900199999
with db_session() as db:
    assert db.transactions.get(txn_id=tid) is None
    code, out, err = cli_runner("txn", "amend", str(tid), "5.00")
    print(out)
    print(err)
    assert code == 4
    assert out == ""
    assert db.transactions.get(txn_id=tid) is None
=== END AC txn-amend-absent ===

=== AC txn-amend-negative-balance ===
Intent: An amend that would leave the account balance below zero exits 3 and keeps the original amount, while an amend landing exactly on zero succeeds. The account holds +10000 and -4000 cents, so lowering the first to 3000 gives -1000 and lowering it to 4000 gives 0.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat = "ZZAM3", "ZZAMC3"
tid_in, tid_out = 900100003, 900100004
too_low, exact = "30.00", "40.00"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=tid_in, date="2026-05-03", account=acct, category=cat, amount=10000, memo="")
    db.transactions.create(txn_id=tid_out, date="2026-05-03", account=acct, category=cat, amount=-4000, memo="")
    code, out, err = cli_runner("txn", "amend", str(tid_in), too_low)
    print(out)
    print(err)
    assert code == 3
    assert out == ""
    assert f(db.transactions.get(txn_id=tid_in), "amount") == 10000
    code, out, err = cli_runner("txn", "amend", str(tid_in), exact)
    print(out)
    print(err)
    assert code == 0
    assert f(db.transactions.get(txn_id=tid_in), "amount") == int(exact.replace(".", ""))
=== END AC txn-amend-negative-balance ===

=== AC txn-amend-invalid-amount ===
Intent: Amounts with three decimals, a zero amount, and a non-numeric amount are rejected with exit 3 and the stored amount is unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

def f(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name)

acct, cat, tid = "ZZAM4", "ZZAMC4", 900100005
original = 10000
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=tid, date="2026-05-04", account=acct, category=cat, amount=original, memo="")
    for bad in ["1.234", "0", "0.00", "abc"]:
        code, out, err = cli_runner("txn", "amend", str(tid), bad)
        print(out)
        print(err)
        assert code == 3
        assert out == ""
        assert f(db.transactions.get(txn_id=tid), "amount") == original
=== END AC txn-amend-invalid-amount ===

=== AC txn-amend-usage ===
Intent: A wrong argument count for txn amend exits 2 with nothing on stdout.

from cli.testing import cli_runner

for args in [("txn", "amend"), ("txn", "amend", "1"), ("txn", "amend", "1", "2.00", "extra")]:
    code, out, err = cli_runner(*args)
    print(out)
    print(err)
    assert code == 2
    assert out == ""
=== END AC txn-amend-usage ===

## User Acceptance

- None.

## Guardrails

- Amounts are integer cents in every layer; floating point is never used for money.
- The balance check runs before the update, so a rejected amend writes nothing.
- Only the amount column changes; no other column is ever written by this command.
- Standard output stays empty on any failure; the diagnostic goes to standard error.
