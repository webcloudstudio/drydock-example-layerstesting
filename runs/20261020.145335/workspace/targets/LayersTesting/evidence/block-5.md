# Evidence: Block 5 · Service (block-5)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4170
- execution id: 20261020.151915.045Z-2a4c9db2

## Stories built
- Write CSV success output and failure diagnostics. (CLI-002) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1145)
- implements: FEATURE-CliOutput.md (SP 1175)
- context: ARCHITECTURE_compact.md (SP 427)
- context: DATABASE_compact.md (SP 427)

## Build directory changes
- cli/output.py
- tests/test_output.py

## Pre-build acceptance observation
- RED: cli-output-csv-shape (FEATURE-CliOutput.md)
  intent: render_csv writes the header and each row as one comma-separated line, in order.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-output-csv-shape.py", line 1, in <module>
        from cli.output import render_csv
    ModuleNotFoundError: No module named 'cli.output'
- RED: cli-output-csv-header-only (FEATURE-CliOutput.md)
  intent: render_csv with no rows writes only the header line.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-output-csv-header-only.py", line 1, in <module>
        from cli.output import render_csv
    ModuleNotFoundError: No module named 'cli.output'
- RED: cli-output-csv-no-padding (FEATURE-CliOutput.md)
  intent: render_csv adds no leading or trailing spaces to any line.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-output-csv-no-padding.py", line 1, in <module>
        from cli.output import render_csv
    ModuleNotFoundError: No module named 'cli.output'
- RED: cli-output-diagnostic-one-line (FEATURE-CliOutput.md)
  intent: render_diagnostic returns the message as exactly one line.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "cli-output-diagnostic-one-line.py", line 1, in <module>
        from cli.output import render_diagnostic
    ModuleNotFoundError: No module named 'cli.output'

## Post-build programmatic acceptance
- PASS: cli-output-csv-shape (FEATURE-CliOutput.md)
  intent: render_csv writes the header and each row as one comma-separated line, in order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-output-csv-header-only (FEATURE-CliOutput.md)
  intent: render_csv with no rows writes only the header line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-output-csv-no-padding (FEATURE-CliOutput.md)
  intent: render_csv adds no leading or trailing spaces to any line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: cli-output-diagnostic-one-line (FEATURE-CliOutput.md)
  intent: render_diagnostic returns the message as exactly one line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.145335/build/LayersTesting/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
The spec for this block is `FEATURE-CliOutput.md`: a new `cli/output.py` with `render_csv` and `render_diagnostic`, plus tests. Nothing in the existing CLI calls these yet, so I'll keep the change to the output module and its tests.That last parametrized header test duplicates the header-only case without adding coverage, so I'll remove it before running.Implemented the CSV output and diagnostic rendering for CLI-002 per `FEATURE-CliOutput.md`. The full suite passes: `sh bin/test.sh` reports 109 passed, exit 0.

Nothing calls these functions yet, so the "init writes nothing" and "failing command writes nothing to stdout" behaviors will only take effect when the command blocks wire them in. I kept this block to the output module.

RESULT: SUCCESS

FILES CHANGED:
- cli/output.py
- tests/test_output.py

SUMMARY:
- `cli/output.py` provides `render_csv(header, rows)`, which joins each line with `,` and ends each with `\n`, with no quoting or padding, and `render_diagnostic(message)`, which returns the message plus one `\n`.
- `tests/test_output.py` has 12 tests. The four declared acceptance assertions (`cli-output-csv-shape`, `cli-output-csv-header-only`, `cli-output-csv-no-padding`, `cli-output-diagnostic-one-line`) are each covered by a test. Extra tests cover one row, many rows, empty fields, values passed through unaltered, no quoting, and the diagnostic edge cases.
- Coverage run for this step: `sh bin/test.sh` (the declared `Suite` for every behavioral story), 109 passed, 0 failed. The terminal `sh sources/run.sh` check is not part of this block.
- Not touched: `sources/`, the Drydock-protected paths, and git history.
