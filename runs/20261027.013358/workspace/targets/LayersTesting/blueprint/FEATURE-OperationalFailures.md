# FEATURE: Operational Failures

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Every command that cannot reach a usable database or read its input file exits 1 with empty standard output and one diagnostic line on standard error. |
| Depends On | FEATURE-CliEntry.md, FEATURE-DatabaseSelection.md, FEATURE-Count.md, FEATURE-LoadAccounts.md, FEATURE-ReportBalances.md |
| Provides | cli.operational |
| Consumes | ledgerlib.config, ledger count, ledger load accounts, ledger report balances |

## Purpose

Exit code 1 means an operational failure: the database is unreachable, the stored file is not a
valid database, or a file named on the command line cannot be read. The grader never checks exit 1,
so this story proves it through the application's own interface. Each such failure writes nothing to
standard output, writes one line to standard error, and performs no write.

## Behavior

| Condition | Command examples | Result |
|-----------|------------------|--------|
| `DATABASE_URL` begins `postgres://` or `postgresql://` | any database command | exit 1, empty stdout, nothing written |
| Database location cannot be opened (parent directory missing, only `init` creates it) | `count`, `report balances` | exit 1, empty stdout, no file created |
| Existing file is not a valid database | `count`, `report balances`, `load accounts <csv>` | exit 1, empty stdout, file bytes unchanged |
| Load file does not exist or is unreadable | `load accounts <missing>` | exit 1, empty stdout, no row stored |

Rules:

- `CliError` subclasses map to exit codes in `cli.main`; this story only ensures the commands raise
  `OperationalError` for the conditions above and never a different code.
- Argument-count (exit 2) checks still run before any database access, so a usage error is never
  reported as exit 1.
- A command that fails operationally has not written anything.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC operational-postgres-refused ===
Intent: A PostgreSQL DSN is refused with exit 1, nothing on standard output, for a read and a load command.

import os

from cli.testing import cli_runner

dsn = "postgresql://nobody@localhost/none"
saved = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = dsn
try:
    code, out, err = cli_runner("count")
    print(out)
    print(err)
    assert code == 1
    assert out == ""
    code2, out2, err2 = cli_runner("report", "balances")
    print(out2)
    print(err2)
    assert code2 == 1
    assert out2 == ""
finally:
    if saved is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = saved
=== END AC operational-postgres-refused ===

=== AC operational-unreachable-database ===
Intent: A database location whose parent directory is missing exits 1 with empty standard output and creates nothing.

import os
import tempfile

from cli.testing import cli_runner

saved = os.environ.get("DATABASE_URL")
with tempfile.TemporaryDirectory() as root:
    target = os.path.join(root, "missing_dir", "ledger.db")
    os.environ["DATABASE_URL"] = target
    try:
        code, out, err = cli_runner("count")
        print(out)
        print(err)
        assert code == 1
        assert out == ""
        code2, out2, err2 = cli_runner("report", "balances")
        print(out2)
        print(err2)
        assert code2 == 1
        assert out2 == ""
        assert not os.path.exists(target)
        assert not os.path.exists(os.path.dirname(target))
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved
=== END AC operational-unreachable-database ===

=== AC operational-invalid-database-file ===
Intent: An existing file that is not a database makes every database command exit 1 with empty standard output and leaves the file unchanged.

import os
import tempfile

from cli.testing import cli_runner

junk = b"this is not a database file, only plain text\n" * 20
saved = os.environ.get("DATABASE_URL")
with tempfile.TemporaryDirectory() as root:
    target = os.path.join(root, "junk.db")
    with open(target, "wb") as fh:
        fh.write(junk)
    csv_path = os.path.join(root, "accounts.csv")
    with open(csv_path, "w", newline="") as fh:
        fh.write("account,name\nJUNK1,Junk One\n")
    os.environ["DATABASE_URL"] = target
    try:
        for args in (("count",), ("report", "balances"), ("load", "accounts", csv_path)):
            code, out, err = cli_runner(*args)
            print(out)
            print(err)
            assert code == 1
            assert out == ""
    finally:
        if saved is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved
    with open(target, "rb") as fh:
        assert fh.read() == junk
=== END AC operational-invalid-database-file ===

=== AC operational-unreadable-load-file ===
Intent: Loading from a file that does not exist exits 1 with empty standard output and stores no account.

import os
import tempfile

from cli.testing import cli_runner
from persistence.testing import db_session

with tempfile.TemporaryDirectory() as root:
    missing = os.path.join(root, "absent.csv")
    with db_session() as db:
        before = len(db.accounts.list())
        code, out, err = cli_runner("load", "accounts", missing)
        print(out)
        print(err)
        assert code == 1
        assert out == ""
        after = len(db.accounts.list())
        assert after == before
=== END AC operational-unreadable-load-file ===

=== AC operational-usage-before-database ===
Intent: A wrong argument count is a usage error with exit 2 even when the database is unusable, so usage is checked before database access.

import os

from cli.testing import cli_runner

saved = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = "postgresql://nobody@localhost/none"
try:
    code, out, err = cli_runner("count", "extra")
    print(out)
    print(err)
    assert code == 2
    assert out == ""
finally:
    if saved is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = saved
=== END AC operational-usage-before-database ===

## User Acceptance

- None.

## Guardrails

- A failing command writes nothing to standard output and exactly one diagnostic line to standard error.
- An operational failure performs no write to the database or to any file.
- No driver is opened outside the shipped persistence library.
- A PostgreSQL DSN is never connected to and never causes a file to be created.
