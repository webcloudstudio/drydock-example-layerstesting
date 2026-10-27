# FEATURE: CSV Output

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Format integer cents and CSV rows exactly as the output contract requires. |
| Depends On | FEATURE-CliEntry.md |
| Provides | ledgerlib.csvout |
| Consumes | cli.main |

## Purpose

One place formats money and rows, so every command prints amounts with exactly two decimal places and
rows with no quoting, no trailing spaces and no thousands separators.

## Interface

`ledgerlib/csvout.py`:

- `format_cents(cents: int) -> str` writes integer cents with exactly two decimals, a leading `-`
  when negative, and no thousands separator. It uses integer arithmetic only, so zero is `0.00`
  and never `-0.00`. A non-integer (including `float` and `bool`) raises `TypeError`.
- `csv_line(fields) -> str` joins fields with commas, with no quoting and no trailing newline;
  `cli.main` adds the `\n` ending.
- `ACCOUNT_HEADER` is `account,name,transactions,balance`.
- `TRANSACTION_HEADER` is `txn_id,date,account,category,amount,memo`.
- `account_row(account, name, transactions, balance_cents) -> str`.
- `transaction_row(txn_id, date, account, category, amount_cents, memo) -> str`.

## Database Interface

- None — this feature formats values and reaches no repository.

## Programmatic Acceptance

=== AC csv-format-examples ===
Intent: Cents format with two decimals, a leading minus, no separators, and zero is never negative.

from ledgerlib.csvout import format_cents

assert format_cents(-1250) == "-12.50"
assert format_cents(0) == "0.00"
assert format_cents(500000) == "5000.00"
assert format_cents(5) == "0.05"
assert format_cents(-5) == "-0.05"
assert format_cents(123456789) == "1234567.89"
=== END AC csv-format-examples ===

=== AC csv-format-roundtrip ===
Intent: For many values the text has the two-decimal shape and its decimal value equals cents divided by one hundred.

import re
from decimal import Decimal

from ledgerlib.csvout import format_cents

shape = re.compile(r"-?\d+\.\d\d")
for cents in range(-250000, 250001, 997):
    text = format_cents(cents)
    assert shape.fullmatch(text), text
    assert "," not in text
    assert Decimal(text) == Decimal(cents) / Decimal(100)
    assert not text.startswith("-0.00")
=== END AC csv-format-roundtrip ===

=== AC csv-format-rejects-float ===
Intent: Money is never formatted from floating point; a float or bool input raises TypeError.

from ledgerlib.csvout import format_cents

for bad in (1.5, 100.0, True):
    raised = False
    try:
        format_cents(bad)
    except TypeError:
        raised = True
    assert raised
=== END AC csv-format-rejects-float ===

=== AC csv-line-join ===
Intent: Rows join with commas, with no quoting and no trailing space or newline.

from ledgerlib.csvout import csv_line

fields = ["alpha", "beta", "gamma"]
line = csv_line(fields)
assert line == ",".join(fields)
assert '"' not in line
assert line == line.rstrip()
assert "\n" not in line
=== END AC csv-line-join ===

=== AC csv-headers ===
Intent: The shared header constants match the output contract's account and transaction columns.

from ledgerlib.csvout import ACCOUNT_HEADER, TRANSACTION_HEADER

assert ACCOUNT_HEADER == "account,name,transactions,balance"
assert TRANSACTION_HEADER == "txn_id,date,account,category,amount,memo"
=== END AC csv-headers ===

=== AC csv-account-row ===
Intent: The account row carries code, name, transaction count and a two-decimal balance in header order.

from decimal import Decimal

from ledgerlib.csvout import ACCOUNT_HEADER, account_row

code = "ZZACCT"
name = "Zz Account"
count = 3
balance = 12345
fields = account_row(code, name, count, balance).split(",")
assert len(fields) == len(ACCOUNT_HEADER.split(","))
assert fields[0] == code
assert fields[1] == name
assert fields[2] == str(count)
assert Decimal(fields[3]) == Decimal(balance) / Decimal(100)
assert fields[3].endswith(fields[3][-3:]) and fields[3][-3] == "."
=== END AC csv-account-row ===

=== AC csv-transaction-row ===
Intent: The transaction row carries id, date, account, category, a signed two-decimal amount and the memo in header order.

from decimal import Decimal

from ledgerlib.csvout import TRANSACTION_HEADER, transaction_row

txn_id = 77
date = "2026-04-05"
account = "ZZACCT"
category = "ZZCAT"
amount = -1234
memo = "zz memo"
line = transaction_row(txn_id, date, account, category, amount, memo)
fields = line.split(",")
assert len(fields) == len(TRANSACTION_HEADER.split(","))
assert fields[0] == str(txn_id)
assert fields[1] == date
assert fields[2] == account
assert fields[3] == category
assert Decimal(fields[4]) == Decimal(amount) / Decimal(100)
assert fields[5] == memo
assert line == line.rstrip("\n")
=== END AC csv-transaction-row ===

## User Acceptance

- None.

## Guardrails

- No floating point is used for money.
- No quoting, no thousands separators and no trailing spaces in any row.
