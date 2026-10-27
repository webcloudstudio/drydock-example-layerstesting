# FEATURE: Validation

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Validate codes, names, memos, amounts, dates and transaction ids per the ledger rules. |
| Depends On | FEATURE-CliEntry.md |
| Provides | ledgerlib.validation |
| Consumes | cli.main |

## Purpose

Every command validates its inputs before its first write. `ledgerlib/validation.py` is the single owner of the field rules in `sources/INSTRUCTIONS.md` Rules 3 to 6 and the transaction id rule. Each function raises `cli.errors.RejectedError` (exit 3) on violation and otherwise returns the validated value.

## Interface

| Function | Returns | Rule |
|----------|---------|------|
| `validate_code(value: str) -> str` | the value | 1 to 12 characters from `A-Z` and `0-9` |
| `validate_name(value: str) -> str` | the value | 1 to 40 characters, no comma, no newline (also used for descriptions) |
| `validate_memo(value: str) -> str` | the value | 0 to 60 characters, no comma, no newline |
| `parse_amount(text: str) -> int` | integer cents | matches `-?DIGITS[.D[D]]`, at most two decimals, never zero |
| `validate_date(text: str) -> str` | the value | real calendar date written `YYYY-MM-DD` |
| `parse_txn_id(text: str) -> int` | the integer | a non-empty string of decimal digits |

## Rules

- Amount parsing uses integer arithmetic on the digit strings only. No `float` or `Decimal`-free shortcut through floating point is permitted at any layer.
- `.5`, `5.`, `1.234`, `+5`, `1e3`, `0`, `0.0` and `0.00` are rejected.
- A date must match the `YYYY-MM-DD` shape exactly and be a real calendar date; `2026-02-30` is rejected.
- A transaction id with a sign, a decimal point, whitespace or no digits is rejected with exit 3.
- Validation reads no database and writes nothing.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC validation-codes ===
Intent: Codes of 1 to 12 characters from A-Z and 0-9 are returned unchanged and every other shape is rejected with exit code 3.

from cli.errors import RejectedError
from ledgerlib import validation

good = "DRAWER1"
longest = "A" * 12
assert validation.validate_code(good) == good
assert validation.validate_code(longest) == longest
for bad in ["", "A" * 13, "drawer1", "AB-C", "A B", "AB,C"]:
    try:
        validation.validate_code(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad code")
=== END AC validation-codes ===

=== AC validation-names-memos ===
Intent: Names are 1 to 40 characters and memos 0 to 60 characters, neither may contain a comma or newline, and violations exit 3.

from cli.errors import RejectedError
from ledgerlib import validation

name = "Front Drawer"
assert validation.validate_name(name) == name
assert validation.validate_name("N" * 40) == "N" * 40
assert validation.validate_memo("") == ""
assert validation.validate_memo("m" * 60) == "m" * 60

bad_names = ["", "N" * 41, "a,b", "a" + chr(10) + "b"]
for bad in bad_names:
    try:
        validation.validate_name(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad name")

bad_memos = ["m" * 61, "a,b", "a" + chr(10) + "b"]
for bad in bad_memos:
    try:
        validation.validate_memo(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad memo")
=== END AC validation-names-memos ===

=== AC validation-amounts ===
Intent: Amounts parse to exact integer cents with at most two decimals and zero, malformed or over-precise amounts are rejected with exit 3.

from cli.errors import RejectedError
from ledgerlib import validation

cases = [
    ("12.50", 1250),
    ("-12.50", -1250),
    ("5", 500),
    ("-5", -500),
    ("1.5", 150),
    ("0.01", 1),
    ("-0.01", -1),
    ("5000.00", 500000),
]
for text, cents in cases:
    got = validation.parse_amount(text)
    assert isinstance(got, int) and not isinstance(got, bool)
    assert got == cents

for bad in ["0", "0.00", "-0", "1.234", "abc", "1.", ".5", "+5", "1e3", "", "1,5"]:
    try:
        validation.parse_amount(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad amount " + bad)
=== END AC validation-amounts ===

=== AC validation-dates ===
Intent: Only real calendar dates written YYYY-MM-DD are accepted, so a nonexistent day or a different shape exits 3.

from cli.errors import RejectedError
from ledgerlib import validation

good = "2026-04-01"
leap = "2024-02-29"
assert validation.validate_date(good) == good
assert validation.validate_date(leap) == leap

for bad in ["2026-02-30", "2026-13-01", "2026-00-10", "2025-02-29", "2026-2-3", "20260401", "2026/04/01", ""]:
    try:
        validation.validate_date(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad date " + bad)
=== END AC validation-dates ===

=== AC validation-txn-id ===
Intent: A transaction id argument must be a string of decimal digits and returns its integer value, otherwise exit 3.

from cli.errors import RejectedError
from ledgerlib import validation

assert validation.parse_txn_id("121") == 121
assert validation.parse_txn_id("1") == 1

for bad in ["", "abc", "-1", "+1", "1.0", " 1", "1 ", "0x10"]:
    try:
        validation.parse_txn_id(bad)
    except RejectedError as exc:
        assert exc.exit_code == 3
    else:
        raise AssertionError("accepted bad id " + repr(bad))
=== END AC validation-txn-id ===

## User Acceptance

- None.

## Guardrails

- No floating point is used to parse, hold or compare money.
- Validation never reads or writes the database.
- Error message wording is not part of the contract; only the exit code is.
