# FEATURE: Code Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validate account and category codes, names, descriptions, and memos before any row is stored. |
| Depends On  | ARCHITECTURE.md |
| Provides    | validate_code, validate_name, validate_memo |

## Purpose

Every command that accepts a code, a name, a description, or a memo runs that value through this
module before any lookup or write. The module lives at `validation.py` in the application root.

## Rules

- `validate_code(value)` accepts 1 to 12 characters, each one of `A-Z` or `0-9`. Lowercase, spaces,
  punctuation, and empty strings are rejected.
- `validate_name(value)` accepts 1 to 40 characters. The same function serves account names and
  category descriptions.
- `validate_memo(value)` accepts 0 to 60 characters. The empty string is valid.
- `validate_name` and `validate_memo` reject any value containing a comma or a newline.
- An accepted value is returned unchanged. A rejected value raises `ValueError`. The command layer
  maps that exception to exit 3 with no change to the database.

## Programmatic Acceptance

=== AC code-accepts-bounds ===
Intent: validate_code returns a one-character code and a twelve-character code unchanged.

from validation import validate_code

shortest = "A"
longest = "Z9Z9Z9Z9Z9Z9"
assert validate_code(shortest) == shortest
assert validate_code(longest) == longest
=== END AC code-accepts-bounds ===

=== AC code-rejects-length ===
Intent: validate_code rejects an empty code and a thirteen-character code.

from validation import validate_code


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


empty = ""
too_long = "A" * 13
assert rejected(validate_code, empty) is True
assert rejected(validate_code, too_long) is True
=== END AC code-rejects-length ===

=== AC code-rejects-characters ===
Intent: validate_code rejects lowercase letters, hyphens, commas, and spaces.

from validation import validate_code


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


for value in ("abc", "A-1", "A,B", "A B"):
    assert rejected(validate_code, value) is True
=== END AC code-rejects-characters ===

=== AC name-bounds ===
Intent: validate_name accepts one and forty characters and rejects zero and forty-one.

from validation import validate_name


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


single = "F"
maximum = "F" * 40
assert validate_name(single) == single
assert validate_name(maximum) == maximum
assert rejected(validate_name, "") is True
assert rejected(validate_name, "F" * 41) is True
=== END AC name-bounds ===

=== AC name-rejects-comma-and-newline ===
Intent: validate_name rejects any name containing a comma or a newline.

from validation import validate_name


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


with_comma = "Front" + chr(44) + "Drawer"
with_newline = "Front" + chr(10) + "Drawer"
assert rejected(validate_name, with_comma) is True
assert rejected(validate_name, with_newline) is True
=== END AC name-rejects-comma-and-newline ===

=== AC memo-bounds ===
Intent: validate_memo accepts the empty memo and a sixty-character memo, and rejects sixty-one characters.

from validation import validate_memo


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


empty = ""
maximum = "m" * 60
assert validate_memo(empty) == empty
assert validate_memo(maximum) == maximum
assert rejected(validate_memo, "m" * 61) is True
=== END AC memo-bounds ===

=== AC memo-rejects-comma-and-newline ===
Intent: validate_memo rejects a memo containing a comma or a newline.

from validation import validate_memo


def rejected(check, value):
    try:
        check(value)
    except ValueError:
        return True
    return False


with_comma = "tape" + chr(44) + "roll"
with_newline = "tape" + chr(10) + "roll"
assert rejected(validate_memo, with_comma) is True
assert rejected(validate_memo, with_newline) is True
=== END AC memo-rejects-comma-and-newline ===

## User Acceptance

- None.

## Guardrails

- The validators never open or read the database.
- Code characters are ASCII `A-Z` and `0-9` only.
- Validation failures raise `ValueError` and never write to standard output.
