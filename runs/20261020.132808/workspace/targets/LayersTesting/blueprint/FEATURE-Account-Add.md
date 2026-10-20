# FEATURE: Account Add

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Add an account with zero transactions and a zero balance through `ledger account add <code> <name>`. |
| Depends On  | DATABASE.md, FEATURE-Code-Validation.md, FEATURE-Amount-Format.md, FEATURE-Command-Transaction.md, FEATURE-CLI-Output.md, FEATURE-CLI-Dispatch.md |
| Provides    | ledger account add <code> <name> |
| Consumes    | accounts.create, accounts.get, accounts.list |

## Purpose

Creates one row in the `accounts` table and prints it.

## Behavior

- The code must be 1 to 12 characters of `A-Z` and `0-9`. The name must be 1 to 40 characters with no comma or newline. A violation exits 3 and changes nothing.
- A code already present exits 3 and changes nothing.
- On success, stdout is the account header row followed by the new row `<code>,<name>,0,0.00`.
- The command runs in one command transaction.

## Programmatic Acceptance

=== AC account-add-prints-and-persists ===
Intent: Adding an account prints the new row with zero transactions and a zero balance, and a later account get returns the same row.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


code_arg = "CASH9"
name_arg = "Event Float"

assert run("init")[0] == 0
code, out, err = run("account", "add", code_arg, name_arg)
assert code == 0
added = list(csv.reader(io.StringIO(out)))
assert added[0] == ["account", "name", "transactions", "balance"]
assert added[1] == [code_arg, name_arg, "0", "0.00"]

code, out, err = run("account", "get", code_arg)
assert code == 0
assert list(csv.reader(io.StringIO(out)))[1] == added[1]
=== END AC account-add-prints-and-persists ===

=== AC account-add-boundary-lengths ===
Intent: An account code of twelve characters and a name of forty characters are accepted and persisted.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


code_arg = "A" * 12
name_arg = "N" * 40

assert run("init")[0] == 0
code, out, err = run("account", "add", code_arg, name_arg)
assert code == 0
assert list(csv.reader(io.StringIO(out)))[1] == [code_arg, name_arg, "0", "0.00"]

code, out, err = run("account", "get", code_arg)
assert code == 0
assert list(csv.reader(io.StringIO(out)))[1] == [code_arg, name_arg, "0", "0.00"]
=== END AC account-add-boundary-lengths ===

=== AC account-add-duplicate-code ===
Intent: Adding a code that already exists exits 3, prints nothing, and leaves exactly one account.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


code_arg = "CASH9"

assert run("init")[0] == 0
assert run("account", "add", code_arg, "Event Float")[0] == 0

code, out, err = run("account", "add", code_arg, "Other Name")
assert code == 3
assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "1"
=== END AC account-add-duplicate-code ===

=== AC account-add-invalid-arguments ===
Intent: Codes and names that violate the field rules each exit 3 and leave the accounts table empty.

import csv
import io
import os
import sys
import tempfile

from cli.testing import cli_runner

os.environ["DATABASE_URL"] = os.path.join(tempfile.mkdtemp(), "ledger.db")


def run(*args):
    code, out, err = cli_runner(*args)
    print(out)
    print(err, file=sys.stderr)
    return code, out, err


rejected = [
    ("lower", "Valid Name"),
    ("", "Valid Name"),
    ("OK2", ""),
    ("OK3", "N" * 41),
    ("A" * 13, "Too Long Code"),
]

assert run("init")[0] == 0
for code_arg, name_arg in rejected:
    code, out, err = run("account", "add", code_arg, name_arg)
    assert code == 3
    assert out == ""

code, out, err = run("count")
counts = {row[0]: row[1] for row in list(csv.reader(io.StringIO(out)))[1:]}
assert counts["accounts"] == "0"
=== END AC account-add-invalid-arguments ===

## User Acceptance

- None.

## Guardrails

- Application code reaches the accounts table only through the `persistence` package operations.
- A rejected add changes nothing and writes nothing to standard output.
- The new account's balance is printed as `0.00`, never computed as a float.
