# Evidence: Block 7 · Service (block-7)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4038
- execution id: 20261020.152133.944Z-8c6cd0c6

## Stories built
- Validate and format amounts as integer cents. (VALID-002) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-ValidateAmount.md (SP 1031)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)

## Build directory changes
- cli/amount.py
- tests/test_amount.py

## Pre-build acceptance observation
- RED: valid-amount-parse-cents (FEATURE-ValidateAmount.md)
  intent: parse_amount converts accepted input text to the expected integer cents.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-amount-parse-cents.py", line 1, in <module>
        from cli.amount import parse_amount
    ModuleNotFoundError: No module named 'cli.amount'
- RED: valid-amount-round-trip (FEATURE-ValidateAmount.md)
  intent: format_amount of parse_amount returns each canonical two-decimal input unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-amount-round-trip.py", line 1, in <module>
        from cli.amount import format_amount, parse_amount
    ModuleNotFoundError: No module named 'cli.amount'
- RED: valid-amount-rejects (FEATURE-ValidateAmount.md)
  intent: parse_amount raises ValueError for zero, excess decimals, malformed, signed-plus, and empty input.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-amount-rejects.py", line 1, in <module>
        from cli.amount import parse_amount
    ModuleNotFoundError: No module named 'cli.amount'
- RED: valid-amount-integer-type (FEATURE-ValidateAmount.md)
  intent: parse_amount returns a Python int, never a float.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-amount-integer-type.py", line 1, in <module>
        from cli.amount import parse_amount
    ModuleNotFoundError: No module named 'cli.amount'

## Post-build programmatic acceptance
- PASS: valid-amount-parse-cents (FEATURE-ValidateAmount.md)
  intent: parse_amount converts accepted input text to the expected integer cents.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-amount-round-trip (FEATURE-ValidateAmount.md)
  intent: format_amount of parse_amount returns each canonical two-decimal input unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-amount-rejects (FEATURE-ValidateAmount.md)
  intent: parse_amount raises ValueError for zero, excess decimals, malformed, signed-plus, and empty input.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-amount-integer-type (FEATURE-ValidateAmount.md)
  intent: parse_amount returns a Python int, never a float.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
I'll start by inspecting the build directory and the existing application files.Existing `cli/` already has `dates.py` and `text_validation.py`, but no `amount.py`. I'll read the CLI code, the tests, and the amount-related checks in `run.sh`.The spec is clear: a new `cli/amount.py` with `parse_amount` and `format_amount`, plus tests. The existing `cli/` modules set the style: module docstring, `from __future__ import annotations`, and pure checks that raise `ValueError`. I'll get a baseline test run before I change anything.Baseline is green at 147 passing. Now I'll write the amount module as specified.Both files are written. Next I'll run the full suite and then the spec's four programmatic acceptance assertions verbatim, since those are the Definition of Done.Amounts now parse to integer cents and format with two decimals. The full suite passes (200 tests, up from 147), and the four acceptance assertions in the spec pass when run verbatim.

I added two files and changed nothing else:

- `cli/amount.py` contains `parse_amount` and `format_amount`. Parsing is integer-only, uses a fullmatch on `-?DIGITS[.D[D]]` with ASCII digits, and rejects zero. Formatting always gives two decimals with a leading `-` when negative.
- `tests/test_amount.py` covers valid and invalid inputs, boundaries, the int-type check, and round-trips.

The story also says a violation exits with status 3. No command handler exists yet, so that exit path isn't wired. It belongs to the command block that will call `parse_amount`.

```text
RESULT: SUCCESS

FILES CHANGED:
- cli/amount.py
- tests/test_amount.py

SUMMARY:
Implemented FEATURE-ValidateAmount.md (VALID-002) as cli/amount.py with parse_amount(text) -> int and format_amount(cents) -> str, using integer arithmetic only. Added tests/test_amount.py: parametrized parse, zero/excess-decimal/malformed rejection, int-type check, format, and round-trip cases, each asserting on return values or raised ValueError. Test runs: `sh bin/test.sh` 200 passed (baseline 147 before this step, 53 added). The four spec ACs (valid-amount-parse-cents, valid-amount-round-trip, valid-amount-rejects, valid-amount-integer-type) were executed verbatim and pass. No staged sources/ asset was run or modified; the staged suite is not invoked by this step's criteria.

BLOCKERS:
- Exit status 3 for a rejected amount is a command-layer behavior; no command handler is built in this block, so it is not wired here and belongs to the block that adds the transaction commands.

<blueprint-decisions>
[{"spec":"FEATURE-ValidateAmount.md","severity":"Low","subject":"Leading zeros in the integer part","decision":"The pattern -?DIGITS[.D[D]] allows any run of digits, so '007' parses to 700 and '00.5' parses to 50. I kept this rather than rejecting leading zeros, because the spec only forbids zero values and excess decimals. Say if leading zeros should be rejected instead."}]
</blueprint-decisions>
```
