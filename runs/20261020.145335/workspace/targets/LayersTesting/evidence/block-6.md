# Evidence: Block 6 · Service (block-6)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4402
- execution id: 20261020.152027.043Z-e5980e8b

## Stories built
- Validate codes, names, descriptions, and memos. (VALID-001) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-ValidateText.md (SP 1406)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)

## Build directory changes
- cli/text_validation.py
- tests/test_text_validation.py

## Pre-build acceptance observation
- RED: valid-text-code-accepts (FEATURE-ValidateText.md)
  intent: check_code returns each 1-to-12-character A-Z/0-9 code unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-code-accepts.py", line 1, in <module>
        from cli.text_validation import check_code
    ModuleNotFoundError: No module named 'cli.text_validation'
- RED: valid-text-code-rejects (FEATURE-ValidateText.md)
  intent: check_code raises ValueError for empty, lowercase, punctuated, spaced, and over-length codes.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-code-rejects.py", line 1, in <module>
        from cli.text_validation import check_code
    ModuleNotFoundError: No module named 'cli.text_validation'
- RED: valid-text-name-accepts (FEATURE-ValidateText.md)
  intent: check_name returns each 1-to-40-character name without comma or newline unchanged.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-name-accepts.py", line 1, in <module>
        from cli.text_validation import check_name
    ModuleNotFoundError: No module named 'cli.text_validation'
- RED: valid-text-name-rejects (FEATURE-ValidateText.md)
  intent: check_name raises ValueError for empty, over-length, comma-bearing, and newline-bearing names.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-name-rejects.py", line 1, in <module>
        from cli.text_validation import check_name
    ModuleNotFoundError: No module named 'cli.text_validation'
- RED: valid-text-memo-accepts (FEATURE-ValidateText.md)
  intent: check_memo returns a 0-to-60-character memo without comma or newline unchanged, including an empty memo.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-memo-accepts.py", line 1, in <module>
        from cli.text_validation import check_memo
    ModuleNotFoundError: No module named 'cli.text_validation'
- RED: valid-text-memo-rejects (FEATURE-ValidateText.md)
  intent: check_memo raises ValueError for over-length, comma-bearing, and newline-bearing memos.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "valid-text-memo-rejects.py", line 1, in <module>
        from cli.text_validation import check_memo
    ModuleNotFoundError: No module named 'cli.text_validation'

## Post-build programmatic acceptance
- PASS: valid-text-code-accepts (FEATURE-ValidateText.md)
  intent: check_code returns each 1-to-12-character A-Z/0-9 code unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-text-code-rejects (FEATURE-ValidateText.md)
  intent: check_code raises ValueError for empty, lowercase, punctuated, spaced, and over-length codes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-text-name-accepts (FEATURE-ValidateText.md)
  intent: check_name returns each 1-to-40-character name without comma or newline unchanged.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-text-name-rejects (FEATURE-ValidateText.md)
  intent: check_name raises ValueError for empty, over-length, comma-bearing, and newline-bearing names.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-text-memo-accepts (FEATURE-ValidateText.md)
  intent: check_memo returns a 0-to-60-character memo without comma or newline unchanged, including an empty memo.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: valid-text-memo-rejects (FEATURE-ValidateText.md)
  intent: check_memo raises ValueError for over-length, comma-bearing, and newline-bearing memos.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
Let me look at an existing module and its test to match the project's idiom, and check the test runner.The existing `dates.py` sets the pattern: a module docstring, a `check_*` function that returns its input or raises `ValueError`, and parametrized pytest tests. I'll follow it for the validators.Now the tests, following `test_dates.py`: parametrized accepts and rejects, with boundaries and the declared maxima.Running the project's declared test command, then the six declared acceptance checks from the spec, each as its own script outside the build tree.All six declared checks pass and the full suite is green. Cleaning up the scratch directory and confirming which files changed.RESULT: SUCCESS

FILES CHANGED:
- cli/text_validation.py
- tests/test_text_validation.py

SUMMARY:
Implemented FEATURE-ValidateText (VALID-001) in `cli/text_validation.py` with `check_code`, `check_name`, and `check_memo`. Each returns its input unchanged or raises `ValueError`, and none of them touch the database.
- `check_code`: 1–12 characters, fullmatch of `[A-Z0-9]`, so lowercase, spaces, punctuation, and a trailing newline are rejected.
- `check_name`: 1–40 characters, no comma, no line break.
- `check_memo`: 0–60 characters, no comma, no line break.

The tests in `tests/test_text_validation.py` are parametrized and cover accepted values, rejected values, the declared maxima and minima, and the empty memo versus empty name. They assert on return values and raised `ValueError`, not on message wording.

Verification:
- `sh bin/test.sh tests/test_text_validation.py`: 38 passed.
- `sh bin/test.sh` (full project suite): 147 passed, exit 0.
- The six declared acceptance checks (valid-text-code-accepts/rejects, name-accepts/rejects, memo-accepts/rejects) were each run as standalone scripts, outside the build tree, against the built module. All six passed.
- No staged `sources/` assets were touched, and no Git history was changed.

blueprint-decisions:
```text
<blueprint-decisions>
[{"spec":"FEATURE-ValidateText.md","severity":"Low","subject":"Carriage return treated as a line break","decision":"The spec forbids only a newline. I also reject a carriage return (\\r) in names and memos, since it is a line break that would corrupt line-oriented CSV and output. Is that acceptable, or should only \\n be rejected?"}]
</blueprint-decisions>
```
