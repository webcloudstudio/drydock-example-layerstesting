# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 4342
- execution id: 20261020.161837.365Z-cfd3a552

## Stories built
- Define the ledger application boundaries and technology usage. (architecture) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 761)
- compass: COMPASS.md (SP 755)
- implements: ARCHITECTURE.md (SP 951)
- stack: common.md (SP 1812)

## Build directory changes
- .gitignore
- CLAUDE.md
- bin/test.sh
- cli/__init__.py
- cli/testing.py
- config.py
- ledger
- persistence/__init__.py
- persistence/db.py
- pyproject.toml
- services.py
- tests/test_architecture.py
- uv.lock

## Pre-build acceptance observation
- RED: architecture-cli-boundary (ARCHITECTURE.md)
  intent: The built CLI exposes the declared lifecycle commands through its public runner.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: architecture-usage-boundary (ARCHITECTURE.md)
  intent: Unknown commands use the declared usage-error exit status and produce no standard output.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: architecture-cli-boundary (ARCHITECTURE.md)
  intent: The built CLI exposes the declared lifecycle commands through its public runner.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: architecture-usage-boundary (ARCHITECTURE.md)
  intent: Unknown commands use the declared usage-error exit status and produce no standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
<reusable-compact filename="ARCHITECTURE.md">
- Python 3.11+ CLI executable: `./ledger <command>`.
- Boundaries: executable, CLI, configuration, validation, services, persistence, test runner.
- Resolve database via `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`.
- Persistence is exclusively through the shipped `persistence` package.
- Commands include lifecycle, loading, accounts, transactions, transfers, and reports.
- Exit codes: 0 success, 1 operational failure, 2 usage error, 3 rejected input/business rule, 4 absent entity.
- Successful commands emit deterministic CSV; failures emit no stdout and diagnostics on stderr.
- Amounts use integer cents; rejected commands perform no writes.
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- .gitignore
- CLAUDE.md
- bin/test.sh
- cli/__init__.py
- cli/testing.py
- config.py
- ledger
- persistence/__init__.py
- persistence/db.py
- pyproject.toml
- services.py
- tests/test_architecture.py
- uv.lock

SUMMARY:
Implemented the Python CLI architecture, configuration resolution, exclusive SQLite persistence boundary, executable `ledger`, and architecture tests. Acceptance checks passed and `bin/test.sh` reports 2 passed.

BLOCKERS:
- None
