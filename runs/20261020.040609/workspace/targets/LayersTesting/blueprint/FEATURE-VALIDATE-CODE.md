# FEATURE: Code Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Account and category codes are accepted only when they are 1 to 12 characters from A-Z and 0-9; any other code is rejected with exit 3. |
| Depends On  | FEATURE-EXIT-CODES.md, FEATURE-TEST-RUNNER.md |
| Provides    | cli.validate.validate_code(value) -> str |
| Consumes    | cli.errors.LedgerError(code, message) |

## Purpose

Codes are the keys of accounts and categories. Every command that accepts a code validates it here
before the code reaches the database.

## Behavior

- `validate_code(value)` returns `value` unchanged when it is 1 to 12 characters, each from `A-Z`
  or `0-9`.
- Any other value raises `LedgerError` with code 3.
- Values are never normalized. Lowercase letters are rejected, not converted to uppercase.

## Programmatic Acceptance

=== AC validate-code-accepts-boundaries ===
Intent: validate_code returns the code unchanged for the shortest, longest, and all-digit valid codes.

from cli.validate import validate_code

shortest = "A"
longest = "ABCDEFGHIJKL"
digits = "0042"
assert validate_code(shortest) == shortest
assert validate_code(longest) == longest
assert validate_code(digits) == digits
=== END AC validate-code-accepts-boundaries ===

=== AC validate-code-rejects-length ===
Intent: validate_code rejects a code longer than 12 characters and an empty code with exit 3.

from cli.errors import LedgerError
from cli.validate import validate_code

def rejected_code(value):
    try:
        validate_code(value)
    except LedgerError as error:
        return error.code
    return None

too_long = "ABCDEFGHIJKLM"
empty = ""
assert rejected_code(too_long) == 3
assert rejected_code(empty) == 3
=== END AC validate-code-rejects-length ===

=== AC validate-code-rejects-lowercase ===
Intent: validate_code rejects lowercase letters with exit 3 and does not normalize them.

from cli.errors import LedgerError
from cli.validate import validate_code

def rejected_code(value):
    try:
        validate_code(value)
    except LedgerError as error:
        return error.code
    return None

lowercase = "cash9"
assert rejected_code(lowercase) == 3
=== END AC validate-code-rejects-lowercase ===

=== AC validate-code-rejects-punctuation ===
Intent: validate_code rejects hyphens, spaces, and trailing newlines with exit 3.

from cli.errors import LedgerError
from cli.validate import validate_code

def rejected_code(value):
    try:
        validate_code(value)
    except LedgerError as error:
        return error.code
    return None

hyphenated = "CASH-9"
spaced = "CASH 9"
newline_ended = "CASH9\n"
assert rejected_code(hyphenated) == 3
assert rejected_code(spaced) == 3
assert rejected_code(newline_ended) == 3
=== END AC validate-code-rejects-punctuation ===

## User Acceptance

- None.

## Guardrails

- A code is never normalized, trimmed, or case-folded by this validator.
- This validator writes nothing to the database.
