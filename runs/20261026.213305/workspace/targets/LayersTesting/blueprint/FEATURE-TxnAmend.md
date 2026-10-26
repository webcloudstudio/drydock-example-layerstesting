# FEATURE: Txn Amend

| Field | Value |
|-------|-------|
| Version | 20261026 V1 |
| Description | Implements `ledger txn amend <id> <amount>`, which changes only a transaction's amount under the non-negative balance rule. |
| Depends On | FEATURE-TxnPost.md, FEATURE-Validation.md, FEATURE-BalanceRules.md, FEATURE-CsvOutput.md, FEATURE-CliFoundation.md, FEATURE-ErrorContract.md, DATABASE.md |
| Provides | ledger txn amend |
| Consumes | ledger.register_command, persistence.open_database, validation.parse_amount, balance_rules.check_final_balances, csv_output.write_rows, ledger_errors.NotFound, ledger_errors.Rejected |

## Purpose

Correct the amount of an existing transaction. Date, account, category and memo never change.

## Behavior

- Invocation: `ledger txn amend <id> <amount>` with exactly two arguments.
- A non-integer id exits 3. An integer id with no stored row exits 4.
- The amount follows the source amount rules (`-?DIGITS[.D[D]]`, at most two decimals, never zero) and is converted to integer cents with integer arithmetic; violations exit 3.
- The account's resulting balance (stored amounts with this row's amount replaced) is checked with `balance_rules.check_final_balances`; a negative result exits 3 and changes nothing.
- Success updates only the amount and writes the header `txn_id,date,account,category,amount,memo` and the updated row.
- Read, check and update run in one database transaction.

## Database Interface

- `FEATURE-TXN-002` — read: get the transaction - supplies: `txn_id` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-003` — read: list the account's transactions for the balance check - supplies: `account` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`
- `FEATURE-TXN-004` — write: change the amount - supplies: `txn_id`, `amount` - returns: `txn_id`, `date`, `account`, `category`, `amount`, `memo`

## Programmatic Acceptance

=== AC txn-amend-success ===
Intent: Amending changes only the amount, prints the updated row, and persists it.

import csv
import io
from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAM1"
cat = "ZQAMC1"
txn_id = 930001
date = "2026-04-01"
memo = "walk in sale"
new_amount = "54.50"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(
        txn_id=txn_id, date=date, account=acct, category=cat, amount=4550, memo=memo
    )
    code, out, err = cli_runner("txn", "amend", str(txn_id), new_amount)
    print(out)
    print(err)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["txn_id", "date", "account", "category", "amount", "memo"]
    assert rows[1] == [str(txn_id), date, acct, cat, new_amount, memo]
    back = db.transactions.get(txn_id=txn_id)
    assert back.amount == int(Decimal(new_amount) * 100)
    assert (back.date, back.account, back.category, back.memo) == (date, acct, cat, memo)
=== END AC txn-amend-success ===

=== AC txn-amend-negative-rejected ===
Intent: An amendment that would leave the balance negative exits 3 and changes nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAM2"
cat = "ZQAMC2"
a_id, b_id = 930021, 930022
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=a_id, date="2026-04-01", account=acct, category=cat, amount=10000, memo="")
    db.transactions.create(txn_id=b_id, date="2026-04-02", account=acct, category=cat, amount=-6000, memo="")
    for amount in ("-100.00", "50.00"):
        code, out, err = cli_runner("txn", "amend", str(a_id), amount)
        print(err)
        assert code == 3, amount
        assert out == "", amount
        assert db.transactions.get(txn_id=a_id).amount == 10000
    code, out, err = cli_runner("txn", "amend", str(b_id), "-100.00")
    assert code == 0
    assert db.transactions.get(txn_id=b_id).amount == -10000
=== END AC txn-amend-negative-rejected ===

=== AC txn-amend-sign-change-allowed ===
Intent: Amending a row to a negative amount succeeds when the account balance stays non-negative.

from decimal import Decimal
from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAM3"
cat = "ZQAMC3"
a_id, b_id = 930031, 930032
new_amount = "-100.00"
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(txn_id=a_id, date="2026-04-01", account=acct, category=cat, amount=20000, memo="")
    db.transactions.create(txn_id=b_id, date="2026-04-02", account=acct, category=cat, amount=5000, memo="")
    code, out, err = cli_runner("txn", "amend", str(b_id), new_amount)
    print(out)
    print(err)
    assert code == 0
    balance = sum(r.amount for r in db.transactions.list(account=acct))
    assert balance == 20000 + int(Decimal(new_amount) * 100)
    assert balance >= 0
=== END AC txn-amend-sign-change-allowed ===

=== AC txn-amend-absent ===
Intent: Amending an absent id exits 4 with nothing on stdout.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    ids = [r.txn_id for r in db.transactions.list()]
    absent = (max(ids) if ids else 0) + 1000
    code, out, err = cli_runner("txn", "amend", str(absent), "5.00")
    print(err)
    assert code == 4
    assert out == ""
=== END AC txn-amend-absent ===

=== AC txn-amend-invalid-amount ===
Intent: Invalid amounts and non-integer ids exit 3 and leave the stored row unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

acct = "ZQAM4"
cat = "ZQAMC4"
txn_id = 930041
original = 2500
with db_session() as db:
    db.accounts.create(account=acct, name="Amend Account")
    db.categories.create(category=cat, description="Amend Category")
    db.transactions.create(
        txn_id=txn_id, date="2026-04-01", account=acct, category=cat, amount=original, memo=""
    )
    for amount in ("0", "0.00", "-0", "1.234", ".5", "+5.00", "abc", "1,000.00"):
        code, out, err = cli_runner("txn", "amend", str(txn_id), amount)
        assert code == 3, amount
        assert out == "", amount
    code, out, err = cli_runner("txn", "amend", "abc", "5.00")
    assert code == 3
    assert out == ""
    assert db.transactions.get(txn_id=txn_id).amount == original
=== END AC txn-amend-invalid-amount ===

## User Acceptance

- None.

## Guardrails

- Only the amount changes; date, account, category and memo are never altered.
- No floating point is used for money at any layer.
- A rejected amendment writes nothing; the balance check precedes the update.
- A failing command writes nothing to stdout and never echoes a DSN or credential.
