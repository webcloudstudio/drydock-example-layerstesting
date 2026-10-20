# FEATURE: Supplied Conformance

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Verifies the completed ledger against the supplied conformance harness. |
| Depends On  | ARCHITECTURE.md, DATABASE.md, FEATURE-TEST-SUITE.md, FEATURE-BALANCE-REPORT.md, FEATURE-CATEGORY-REPORT.md, FEATURE-MONTHLY-REPORT.md |
| Provides    | complete supplied conformance verification |
| Consumes    | `./ledger executable`, `bin/test.sh`, ledger reports and mutations |

## Purpose

The supplied `sources/run.sh` harness is the terminal verification of the completed product. It is executed unchanged from the application root with all supplied seed files available.

## Programmatic Acceptance

=== AC supplied-conformance ===
Intent: The completed ledger passes the authoritative supplied conformance harness.
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
=== END AC supplied-conformance ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, filter, or reinterpret `sources/run.sh` or supplied seed files.
- The harness is the sole terminal release verification command.
- The application must compute results from the database rather than embedding report answers.
