# FEATURE: Operational Errors

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Map unreachable databases, missing tables, and unreadable input files to exit 1 with no change. |
| Depends On  | ARCHITECTURE.md, FEATURE-Database-Location.md, FEATURE-CLI-Dispatch.md |
| Consumes    | resolve_database_location() |

## Purpose

Operational failures are distinct from usage errors and rejections. When the database cannot be
reached, a non-`init` command finds its tables missing, or an input file cannot be read, the
command exits 1, writes nothing to standard output, writes one diagnostic line to standard error,
and changes nothing.

## Interface

- Exit code `1` for every operational failure.
- Standard output is empty on failure.
- Standard error carries exactly one non-empty diagnostic line.

## Programmatic Acceptance

=== AC dberr-unreachable ===
Intent: A database location under a missing directory exits 1 with empty stdout and one stderr line.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    dsn = str(Path(tmp) / "absent-dir" / "ledger.db")
    saved = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = dsn
    try:
        code, out, err = cli_runner("count")
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved
print(out)
print(err, file=sys.stderr)
lines = [line for line in err.splitlines() if line.strip()]
assert code == 1
assert out == ""
assert len(lines) == 1
=== END AC dberr-unreachable ===

=== AC dberr-missing-tables ===
Intent: A non-init command against an empty database with no tables exits 1 with empty stdout.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "empty.db"
    db.touch()
    saved = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(db)
    try:
        code, out, err = cli_runner("count")
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved
print(out)
print(err, file=sys.stderr)
lines = [line for line in err.splitlines() if line.strip()]
assert code == 1
assert out == ""
assert len(lines) == 1
=== END AC dberr-missing-tables ===

=== AC dberr-unreadable-input ===
Intent: A load whose CSV file does not exist exits 1 with empty stdout.

import os
import sys
import tempfile
from pathlib import Path

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "empty.db"
    db.touch()
    missing = str(Path(tmp) / "absent.csv")
    saved = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = str(db)
    try:
        code, out, err = cli_runner("load", "accounts", missing)
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved
print(out)
print(err, file=sys.stderr)
assert code == 1
assert out == ""
=== END AC dberr-unreadable-input ===

## User Acceptance

- None.

## Guardrails

- Operational failures never write to standard output.
- A failed command leaves every table exactly as it was.
