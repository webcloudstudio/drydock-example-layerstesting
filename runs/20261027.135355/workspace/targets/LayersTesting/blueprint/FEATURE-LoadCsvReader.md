# FEATURE: Load CSV Reader

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Shared reader that opens a CSV file named on the command line, checks its header, and returns numbered rows. |
| Depends On | ARCHITECTURE.md, FEATURE-CliEntry.md |
| Provides | ledger_core.csvio |
| Consumes | ledger, cli.registry |

## Purpose

The three `ledger load <table> <csv>` commands share one reader so that file handling, header
checking, and the exit codes for unreadable files and malformed rows are identical. The reader
only reads: it never touches the database and never writes.

## Interface

`ledger_core.csvio.read_rows(path, header)`

- `path` is the file path named on the command line; `header` is the sequence of column names the
  table requires, in order.
- Returns a list of `(line_number, fields)` tuples, one per data row, in file order. `line_number`
  is the 1-based line of the file (the header is line 1, so the first data row is line 2). `fields`
  is a list of strings exactly as parsed by the `csv` module.
- A file that is missing or cannot be read or decoded raises `Operational` (exit 1).
- A header that differs from `header` in names or order, an empty file, or a data row whose field
  count differs from `len(header)` raises `Rejected` (exit 3), with a diagnostic naming the line.
- A file with a valid header and no data rows returns an empty list.
- Blank lines are not data rows and are skipped.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC csvio-reads-numbered-rows ===
Intent: read_rows returns every data row in file order with 1-based file line numbers and the parsed fields, for a file whose header matches.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from ledger_core.csvio import read_rows

header = ["account", "name"]
rows = [["ZZR1", "First Row"], ["ZZR2", "Second Row"], ["ZZR3", "Third Row"]]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "in.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    got = read_rows(path, header)
    assert len(got) == len(rows)
    for i, (line_no, fields) in enumerate(got):
        assert line_no == i + 2
        assert list(fields) == rows[i]
=== END AC csvio-reads-numbered-rows ===

=== AC csvio-header-only-is-empty ===
Intent: a file with a matching header and no data rows yields an empty list rather than an error.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from ledger_core.csvio import read_rows

header = ["category", "description"]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "in.csv")
    with open(path, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow(header)
    assert list(read_rows(path, header)) == []
=== END AC csvio-header-only-is-empty ===

=== AC csvio-missing-file-operational ===
Intent: an unreadable path raises the Operational error, which the CLI maps to exit 1.
Requires: executable=python3; scope=test

import os
import tempfile
from ledger_core.csvio import read_rows

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "does-not-exist.csv")
    try:
        read_rows(path, ["account", "name"])
    except Exception as exc:
        assert type(exc).__name__ == "Operational"
    else:
        raise AssertionError("expected Operational")
=== END AC csvio-missing-file-operational ===

=== AC csvio-bad-header-rejected ===
Intent: a header with the wrong names, the wrong order, or no content raises Rejected, which the CLI maps to exit 3.
Requires: executable=python3; scope=test

import csv
import os
import tempfile
from ledger_core.csvio import read_rows

header = ["account", "name"]
bad_headers = [["name", "account"], ["account"], ["account", "name", "extra"], ["code", "name"]]
with tempfile.TemporaryDirectory() as d:
    for i, bad in enumerate(bad_headers):
        path = os.path.join(d, f"bad{i}.csv")
        with open(path, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerow(bad)
        try:
            read_rows(path, header)
        except Exception as exc:
            assert type(exc).__name__ == "Rejected"
        else:
            raise AssertionError("expected Rejected for header %r" % (bad,))
    empty = os.path.join(d, "empty.csv")
    open(empty, "w").close()
    try:
        read_rows(empty, header)
    except Exception as exc:
        assert type(exc).__name__ == "Rejected"
    else:
        raise AssertionError("expected Rejected for an empty file")
=== END AC csvio-bad-header-rejected ===

=== AC csvio-wrong-field-count-rejected ===
Intent: a data row with too few or too many fields raises Rejected even when the header is valid.
Requires: executable=python3; scope=test

import os
import tempfile
from ledger_core.csvio import read_rows

header = ["account", "name"]
bodies = ["ZZR1\n", "ZZR1,Name,Extra\n"]
with tempfile.TemporaryDirectory() as d:
    for i, body in enumerate(bodies):
        path = os.path.join(d, f"row{i}.csv")
        with open(path, "w", newline="") as fh:
            fh.write(",".join(header) + "\n" + body)
        try:
            read_rows(path, header)
        except Exception as exc:
            assert type(exc).__name__ == "Rejected"
        else:
            raise AssertionError("expected Rejected for body %r" % body)
=== END AC csvio-wrong-field-count-rejected ===

=== AC csvio-load-missing-file-exit-1 ===
Intent: through the CLI, a load naming an unreadable file exits 1, writes nothing to stdout, and stores nothing.
Requires: executable=python3; scope=test

import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "missing.csv")
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", path)
        assert code == 1
        assert out == ""
        assert len(db.accounts.list()) == before
=== END AC csvio-load-missing-file-exit-1 ===

## User Acceptance

- None.

## Guardrails

- The reader never writes to the database or to any file.
- The reader never opens a database driver.
- Diagnostics go to standard error only; nothing is written to standard output.
