# FEATURE: Text Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Validate account and category codes, names, descriptions, and memos. |
| Depends On  | FEATURE-CliEntry.md, ARCHITECTURE.md |
| Provides    | check_code, check_name, check_memo |

## Purpose

Rules 3 and 4 of the cash ledger: codes, names, descriptions, and memos are checked before any
command writes to the database. A violation is reported by the command layer with exit code 3.

## Interface

- `cli.text_validation.check_code(text: str) -> str` returns `text` when it is 1 to 12 characters
  from `A-Z` and `0-9`; otherwise raises `ValueError`.
- `cli.text_validation.check_name(text: str) -> str` returns `text` when it is 1 to 40 characters
  and contains no comma and no newline; otherwise raises `ValueError`. Used for names and
  descriptions.
- `cli.text_validation.check_memo(text: str) -> str` returns `text` when it is 0 to 60 characters
  and contains no comma and no newline; otherwise raises `ValueError`.

## Behavior

- Validators never normalize case or whitespace; a lowercase code is rejected.
- Validators do not touch the database.

## Programmatic Acceptance

=== AC valid-text-code-accepts ===
Intent: check_code returns each 1-to-12-character A-Z/0-9 code unchanged.

from cli.text_validation import check_code

samples = ["A", "AB12", "Z9", "A" * 12]
accepted = [check_code(code) for code in samples]
assert accepted == samples
=== END AC valid-text-code-accepts ===

=== AC valid-text-code-rejects ===
Intent: check_code raises ValueError for empty, lowercase, punctuated, spaced, and over-length codes.

from cli.text_validation import check_code

samples = ["", "ab", "A-1", "A B", "A" * 13]
rejected = []
for code in samples:
    try:
        check_code(code)
    except ValueError:
        rejected.append(code)
assert rejected == samples
=== END AC valid-text-code-rejects ===

=== AC valid-text-name-accepts ===
Intent: check_name returns each 1-to-40-character name without comma or newline unchanged.

from cli.text_validation import check_name

samples = ["N", "Front Drawer", "N" * 40]
accepted = [check_name(name) for name in samples]
assert accepted == samples
=== END AC valid-text-name-accepts ===

=== AC valid-text-name-rejects ===
Intent: check_name raises ValueError for empty, over-length, comma-bearing, and newline-bearing names.

from cli.text_validation import check_name

samples = ["", "N" * 41, "a,b", "a\nb"]
rejected = []
for name in samples:
    try:
        check_name(name)
    except ValueError:
        rejected.append(name)
assert rejected == samples
=== END AC valid-text-name-rejects ===

=== AC valid-text-memo-accepts ===
Intent: check_memo returns a 0-to-60-character memo without comma or newline unchanged, including an empty memo.

from cli.text_validation import check_memo

samples = ["", "walk in sale", "m" * 60]
accepted = [check_memo(memo) for memo in samples]
assert accepted == samples
=== END AC valid-text-memo-accepts ===

=== AC valid-text-memo-rejects ===
Intent: check_memo raises ValueError for over-length, comma-bearing, and newline-bearing memos.

from cli.text_validation import check_memo

samples = ["m" * 61, "a,b", "a\nb"]
rejected = []
for memo in samples:
    try:
        check_memo(memo)
    except ValueError:
        rejected.append(memo)
assert rejected == samples
=== END AC valid-text-memo-rejects ===

## User Acceptance

- None.

## Guardrails

- A validator never accepts a value the Rules section rejects.
- Validators raise ValueError only; the command layer maps the failure to exit code 3.
- Validators never read or write the database.
