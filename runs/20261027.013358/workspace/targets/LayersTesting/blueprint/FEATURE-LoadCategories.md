# FEATURE: Load Categories

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger load categories <csv>` as an all-or-nothing bulk load of categories. |
| Depends On | FEATURE-LoadAccounts.md, FEATURE-Validation.md, DATABASE.md |
| Provides | ledger load categories |
| Consumes | ledger load accounts, ledgerlib.validation |

## Purpose

Load category records from a CSV file into the ledger. The whole file is accepted or none of it is stored.

## Interface

`ledger load categories <csv>` adds the `categories` handler to the per-table registry in `cli/commands/load.py` created by the accounts load story.

Output on success, as CSV with `\n` endings:

```text
table,loaded
categories,<rows>
```

## Behavior

1. The file must be readable. An unreadable or missing file is an operational failure (exit 1, nothing on stdout).
2. The header row must be exactly `category,description`. Any other header is rejected (exit 3).
3. Every data row has the same field count as the header, else the file is rejected (exit 3).
4. Each `category` is a code of 1 to 12 characters from `A-Z` and `0-9`. Each `description` is 1 to 40 characters with no comma or newline.
5. A code repeated within the file, or already stored, is rejected (exit 3).
6. Every check completes before the first write. Writes happen in one database transaction, so a rejected file stores nothing.
7. A file with a valid header and no data rows loads zero rows, prints `categories,0` and exits 0.
8. A missing path argument is a usage error (exit 2).

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC load-categories-success ===
Intent: A valid categories file loads in full, reports the row count, and every row reads back through the public store interface.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

def write_csv(directory, name, rows):
    path = os.path.join(directory, name)
    with open(path, "w", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(rows)
    return path

data = [["ZZLC1", "Load Cat One"], ["ZZLC2", "Load Cat Two"], ["ZZLC3", "Load Cat Three"]]
with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "cats.csv", [["category", "description"]] + data)
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed == [["table", "loaded"], ["categories", str(len(data))]]
    for cat, desc in data:
        row = db.categories.get(category=cat)
        assert row is not None
        assert row.description == desc
=== END AC load-categories-success ===

=== AC load-categories-header-only ===
Intent: A file with a valid header and no data rows loads zero rows and exits zero.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "empty.csv")
        with open(path, "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerow(["category", "description"])
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed == [["table", "loaded"], ["categories", "0"]]
=== END AC load-categories-header-only ===

=== AC load-categories-atomic-rejection ===
Intent: A file whose last row has an invalid code is rejected with exit 3 and none of its valid earlier rows are stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

good = [["ZZLA1", "Atomic One"], ["ZZLA2", "Atomic Two"]]
bad = ["zzbad", "Atomic Bad"]
with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "atomic.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerows(good)
            w.writerow(bad)
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 3
    assert out == ""
    for cat, _ in good:
        assert db.categories.get(category=cat) is None
=== END AC load-categories-atomic-rejection ===

=== AC load-categories-bad-header ===
Intent: A file whose header differs from the table columns is rejected with exit 3 and stores nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

cat = "ZZLH1"
with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "hdr.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "desc"])
            w.writerow([cat, "Header Test"])
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 3
    assert out == ""
    assert db.categories.get(category=cat) is None
=== END AC load-categories-bad-header ===

=== AC load-categories-field-count ===
Intent: A data row whose field count differs from the header is rejected with exit 3 and the whole file is not stored.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

first = "ZZLF1"
with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "count.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerow([first, "Count One"])
            w.writerow(["ZZLF2"])
        code, out, err = cli_runner("load", "categories", path)
    print(out, err)
    assert code == 3
    assert out == ""
    assert db.categories.get(category=first) is None
=== END AC load-categories-field-count ===

=== AC load-categories-duplicates ===
Intent: A code repeated within the file, and a code already stored, are each rejected with exit 3 without changing stored data.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

dup = "ZZLD1"
stored = "ZZLD2"
stored_desc = "Stored Desc"
with db_session() as db:
    db.categories.create(category=stored, description=stored_desc)
    with tempfile.TemporaryDirectory() as tmp:
        p1 = os.path.join(tmp, "dup_in_file.csv")
        with open(p1, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerow([dup, "First"])
            w.writerow([dup, "Second"])
        code1, out1, err1 = cli_runner("load", "categories", p1)
        p2 = os.path.join(tmp, "dup_stored.csv")
        with open(p2, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "description"])
            w.writerow(["ZZLD3", "New One"])
            w.writerow([stored, "Replacement"])
        code2, out2, err2 = cli_runner("load", "categories", p2)
    print(out1, err1, out2, err2)
    assert code1 == 3
    assert code2 == 3
    assert out1 == "" and out2 == ""
    assert db.categories.get(category=dup) is None
    assert db.categories.get(category="ZZLD3") is None
    kept = db.categories.get(category=stored)
    assert kept is not None
    assert kept.description == stored_desc
=== END AC load-categories-duplicates ===

=== AC load-categories-invalid-fields ===
Intent: An over-long code, an empty description and a description containing a comma (quoted in the file) are each rejected with exit 3 and store nothing.

import csv
import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

cases = [
    ["ZZ" + "A" * 11, "Too Long Code"],
    ["ZZLV1", ""],
    ["ZZLV2", "x" * 41],
    ["ZZLV3", "has, comma"],
]
with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        for i, row in enumerate(cases):
            path = os.path.join(tmp, f"bad{i}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["category", "description"])
                w.writerow(row)
            code, out, err = cli_runner("load", "categories", path)
            print(row, code, out, err)
            assert code == 3
            assert out == ""
            assert db.categories.get(category=row[0]) is None
=== END AC load-categories-invalid-fields ===

=== AC load-categories-unreadable-file ===
Intent: A path that cannot be read is an operational failure with exit 1 and nothing on standard output.

import os
import tempfile
from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    with tempfile.TemporaryDirectory() as tmp:
        missing = os.path.join(tmp, "no_such_file.csv")
        code, out, err = cli_runner("load", "categories", missing)
    print(out, err)
    assert code == 1
    assert out == ""
=== END AC load-categories-unreadable-file ===

=== AC load-categories-usage ===
Intent: A categories load with no file argument is a usage error with exit 2 and nothing on standard output.

from cli.testing import cli_runner
from persistence.testing import db_session

with db_session() as db:
    code, out, err = cli_runner("load", "categories")
    print(out, err)
    assert code == 2
    assert out == ""
=== END AC load-categories-usage ===

## User Acceptance

- None.

## Guardrails

- A rejected load stores none of the file's rows.
- Application code does not read `sources/seed_categories.csv`; seed files reach the database only through `ledger load`.
- Only the generated persistence package touches the database; no driver import in load code.
- Diagnostics go to standard error and never to standard output.
