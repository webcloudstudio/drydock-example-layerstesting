# FEATURE: Ledger Core

| Field | Value |
|-------|-------|
| Version | 20261025 V1 |
| Description | Shared integer-cent amount parsing and formatting, field and date validators, and the projected-balance guard. |
| Depends On | ARCHITECTURE.md, DATABASE.md, FEATURE-CliEntry.md |
| Provides | cli.core.parse_amount, cli.core.format_amount, cli.core.validate_code, cli.core.validate_text, cli.core.validate_name, cli.core.validate_memo, cli.core.validate_date, cli.core.account_balance, cli.core.balance_guard |

## Purpose

Every command shares the same input rules. They live in `cli/core.py` so that no command repeats or contradicts them. All validators raise `cli.errors.Rejected` (exit 3) and perform no database write.

## Rules

| Function | Contract |
|----------|----------|
| `parse_amount(text) -> int` | Accepts only ASCII text matching `-?DIGITS[.D[D]]`. Returns integer cents using integer arithmetic only. Zero (such as `0`, `0.00`, `-0.0`) is rejected. More than two decimals, a missing integer part, a plus sign, spaces, or a thousands separator is rejected. |
| `format_amount(cents) -> str` | Exactly two decimals, a leading `-` when negative, no thousands separator. `0` prints as the zero amount with two decimals. |
| `validate_code(text) -> str` | 1 to 12 characters from `A-Z` and `0-9`. |
| `validate_text(text, min_len, max_len) -> str` | Length within bounds; no comma, `\n`, or `\r`. |
| `validate_name(text)` | `validate_text` with 1 to 40 characters. Used for account names and category descriptions. |
| `validate_memo(text)` | `validate_text` with 0 to 60 characters. |
| `validate_date(text) -> str` | Matches `YYYY-MM-DD` with four-digit year, two-digit month and day, and is a real calendar date. A date such as the thirtieth of February is rejected. |
| `account_balance(db, account) -> int` | Sum of the account's transaction amounts, read with `db.transactions.list(account=...)`. Zero when it has none. |
| `balance_guard(db, deltas) -> None` | `deltas` maps account code to a net change in cents. Computes each account's balance after applying its delta and raises `Rejected` when any resulting balance is below zero. It never writes. |

Commands call `balance_guard` with the full change set before their first write. A load passes the summed delta per account for the whole file; a transfer passes both accounts; amend passes the new amount minus the old; delete passes the negated old amount.

## Database Interface


- None — persistence is owned by DATABASE.md, FEATURE-AccountAdd.md, FEATURE-AccountDelete.md, FEATURE-AccountGet.md, FEATURE-AccountRename.md, FEATURE-Init.md, FEATURE-TxnAmend.md, FEATURE-TxnDelete.md, FEATURE-TxnGet.md, FEATURE-TxnPost.md.

## Programmatic Acceptance

=== AC core-parse-amount ===
Intent: parse_amount converts valid decimal text to integer cents.

from cli.core import parse_amount

assert parse_amount("12.50") == 1250
assert parse_amount("-12.50") == -1250
assert parse_amount("5") == 500
assert parse_amount("7.5") == 750
assert parse_amount("0.01") == 1
assert parse_amount("5000.00") == 500000
assert isinstance(parse_amount("1.25"), int)
=== END AC core-parse-amount ===

=== AC core-parse-amount-rejects ===
Intent: parse_amount rejects zero, excess decimals, and malformed text with Rejected.

from cli.core import parse_amount
from cli.errors import Rejected

def rejected(text):
    try:
        parse_amount(text)
    except Rejected:
        return True
    return False

for bad in ["0", "0.00", "-0.0", "1.234", "", ".5", "1.", "abc", "+1.00", "1,000.00", "1 .00", "--1"]:
    assert rejected(bad), bad
=== END AC core-parse-amount-rejects ===

=== AC core-format-amount ===
Intent: format_amount prints two decimals, a leading minus when negative, and no thousands separator.

from cli.core import format_amount, parse_amount

assert format_amount(-1250) == "-12.50"
assert format_amount(0) == "0.00"
assert format_amount(500000) == "5000.00"
assert format_amount(5) == "0.05"
assert "," not in format_amount(123456789)
for cents in [1, -1, 99, 100, -100, 123456, -987654, 500000]:
    assert parse_amount(format_amount(cents)) == cents
=== END AC core-format-amount ===

=== AC core-validate-code ===
Intent: validate_code accepts 1 to 12 characters of A-Z and 0-9 and rejects everything else.

from cli.core import validate_code
from cli.errors import Rejected

good = "A" * 12
assert validate_code(good) == good
assert validate_code("DRAWER1") == "DRAWER1"

def rejected(text):
    try:
        validate_code(text)
    except Rejected:
        return True
    return False

for bad in ["", "A" * 13, "drawer", "AB-C", "A B", "A,B", "ÅB"]:
    assert rejected(bad), bad
=== END AC core-validate-code ===

=== AC core-validate-text ===
Intent: Names and memos enforce their length bounds and forbid comma and newline.

from cli.core import validate_memo, validate_name
from cli.errors import Rejected

def rejected(fn, text):
    try:
        fn(text)
    except Rejected:
        return True
    return False

name40 = "n" * 40
memo60 = "m" * 60
assert validate_name(name40) == name40
assert validate_memo(memo60) == memo60
assert validate_memo("") == ""
assert rejected(validate_name, "")
assert rejected(validate_name, "n" * 41)
assert rejected(validate_memo, "m" * 61)
for bad in ["a,b", "a\nb", "a\rb"]:
    assert rejected(validate_name, bad)
    assert rejected(validate_memo, bad)
=== END AC core-validate-text ===

=== AC core-validate-date ===
Intent: validate_date accepts real YYYY-MM-DD dates and rejects impossible or malformed ones.

from cli.core import validate_date
from cli.errors import Rejected

def rejected(text):
    try:
        validate_date(text)
    except Rejected:
        return True
    return False

for good in ["2026-04-01", "2028-02-29", "2026-12-31"]:
    assert validate_date(good) == good
for bad in ["2026-02-30", "2026-13-01", "2027-02-29", "2026-4-1", "20260401", "2026/04/01", "", "2026-04-01x"]:
    assert rejected(bad), bad
=== END AC core-validate-date ===

=== AC core-balance-guard ===
Intent: balance_guard accepts a change that keeps every balance at or above zero, rejects one that goes below, and writes nothing.

from cli.core import account_balance, balance_guard
from cli.errors import Rejected
from persistence.testing import db_session

with db_session() as db:
    acct = "ACPTBG1"
    cat = "ACPTBGC"
    db.accounts.create(account=acct, name="Guard Account")
    db.categories.create(category=cat, description="Guard Category")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    funded = 1000
    db.transactions.create(
        txn_id=new_id, date="2026-06-01", account=acct, category=cat, amount=funded, memo=""
    )
    rows_before = len(db.transactions.list(account=acct))
    assert account_balance(db, acct) == funded
    balance_guard(db, {acct: -funded})
    try:
        balance_guard(db, {acct: -funded - 1})
        raised = False
    except Rejected:
        raised = True
    assert raised
    assert len(db.transactions.list(account=acct)) == rows_before
    assert account_balance(db, acct) == funded
=== END AC core-balance-guard ===

=== AC core-balance-guard-multi-account ===
Intent: balance_guard rejects when any one account in the change set would go negative.

from cli.core import balance_guard
from cli.errors import Rejected
from persistence.testing import db_session

with db_session() as db:
    rich = "ACPTBM1"
    poor = "ACPTBM2"
    cat = "ACPTBMC"
    db.accounts.create(account=rich, name="Rich")
    db.accounts.create(account=poor, name="Poor")
    db.categories.create(category=cat, description="Multi")
    new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
    db.transactions.create(
        txn_id=new_id, date="2026-06-02", account=rich, category=cat, amount=5000, memo=""
    )
    balance_guard(db, {rich: -5000, poor: 5000})
    try:
        balance_guard(db, {rich: 100, poor: -1})
        raised = False
    except Rejected:
        raised = True
    assert raised
=== END AC core-balance-guard-multi-account ===

=== AC core-no-floating-point ===
Intent: The core module uses no float literal and no float conversion.

import ast

with open("cli/core.py", encoding="utf-8") as fh:
    tree = ast.parse(fh.read())
literals = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)]
names = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "float"]
assert literals == []
assert names == []
=== END AC core-no-floating-point ===

## User Acceptance

- None.

## Guardrails

- Money is integer cents; no floating point, `Decimal` shortcuts via float, or string-rounding tricks.
- Validators and the guard never write to the database.
- Error messages are free text; only the exit code is a contract.
