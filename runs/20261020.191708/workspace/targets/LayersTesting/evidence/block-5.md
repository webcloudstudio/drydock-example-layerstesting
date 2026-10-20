# Evidence: Block 5 · Service (block-5)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4082
- execution id: 20261020.192935.145Z-8a2dff8c

## Stories built
- Validate command names, tables, reports, and argument counts. (cli-validation) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-CLI-Validation.md (SP 592)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- tests/test_cli_validation.py

## Pre-build acceptance observation
- RED: cli-validation-unknown-command (FEATURE-CLI-Validation.md)
  intent: An unknown command is rejected as a usage error.
  return code: 2
- RED: cli-validation-unknown-report (FEATURE-CLI-Validation.md)
  intent: An unknown report is rejected as a usage error.
  return code: 2
- RED: cli-validation-argument-count (FEATURE-CLI-Validation.md)
  intent: A documented command with an incorrect argument count is rejected as a usage error.
  return code: 2
- GREEN (prepassed): cli-validation-help (FEATURE-CLI-Validation.md)
  intent: Help is available for the command dispatcher and documented command families.
  return code: 0

## Post-build programmatic acceptance
- PASS: cli-validation-unknown-command (FEATURE-CLI-Validation.md)
  intent: An unknown command is rejected as a usage error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-validation-unknown-report (FEATURE-CLI-Validation.md)
  intent: An unknown report is rejected as a usage error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-validation-argument-count (FEATURE-CLI-Validation.md)
  intent: A documented command with an incorrect argument count is rejected as a usage error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-validation-help (FEATURE-CLI-Validation.md)
  intent: Help is available for the command dispatcher and documented command families.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- tests/test_cli_validation.py

SUMMARY:
Implemented CLI usage/help status handling. All tests pass; staged harness reports 43/43 passed.

BLOCKERS:
- None
