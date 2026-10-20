# FEATURE: Conformance Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Runs the supplied ledger conformance harness as the terminal release verification. |
| Depends On  | ARCHITECTURE.md, FEATURE-Test-Runner.md, FEATURE-Balance-Reports.md, FEATURE-Category-Reports.md, FEATURE-Monthly-Reports.md |
| Provides    | full supplied conformance verification |
| Consumes    | all ledger command capabilities |

## Purpose

The supplied `sources/run.sh` harness is staged unchanged and executed from the completed application root. Its exit status is the release conformance verdict.

## Programmatic Acceptance

=== AC supplied-conformance-suite ===
Intent: The supplied conformance harness executes all authoritative checks and exits successfully.
Suite: full

import subprocess

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC supplied-conformance-suite ===

## User Acceptance

- None.

## Guardrails

- Run `sources/run.sh` unfiltered as the terminal verification.
- Preserve the supplied harness and seed files byte-for-byte.
- Treat the harness exit status as authoritative; do not replace it with output scraping or hardcoded report values.
