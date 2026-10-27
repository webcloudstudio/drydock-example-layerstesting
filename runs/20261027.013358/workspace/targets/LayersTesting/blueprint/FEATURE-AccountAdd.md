# FEATURE: Account Add

| Field | Value |
|-------|-------|
| Version | 20261027 V1 |
| Description | Implements `ledger account add <code> <name>` creating a new account with a zero balance. |
| Depends On | FEATURE-LedgerRules.md, FEATURE-Validation.md, FEATURE-CsvOutput.md, FEATURE-LoadCategories.md, DATABASE.md |
| Provides | ledger account add |
| Consumes | ledgerlib.rules, ledgerlib.validation, ledgerlib.csvout |

## Purpose

Add one account. This story creates `cli/commands/account.py` with the verb table that later account verbs extend.

## Interface

`ledger account add <code> <name>`. Output:

```text
account,name,transactions,balance
<code>,<name>,0,0.00
```

## Behavior

1. `account` with an unknown verb, or `add` with other than exactly two arguments, is a usage error (exit 2).
2. `code` is 1 to 12 characters from `A-Z` and `0-9`; `name` is 1 to 40 characters with no comma or newline. Violations exit 3.
3. A code already stored is rejected (exit 3) and the stored account is unchanged.
4. All checks precede the write. The printed row is read back from storage.

## Database Interface

- None — persistence is owned by DATABASE.md.

## Programmatic Acceptance

=== AC acct-add-success ===
Intent: Adding an account prints the new row with zero transactions and balance 0.00, and the account reads back from the store.

import csv
from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZAA1"
name = "Add Account One"
with db_session() as db:
    code, out, err = cli_runner("account", "add", code_arg, name)
    print(out, err)
    assert code == 0
    parsed = list(csv.reader(out.splitlines()))
    assert parsed[0] == ["account", "name", "transactions", "balance"]
    assert parsed[1] == [code_arg, name, "0", "0.00"]
    assert len(parsed) == 2
    row = db.accounts.get(account=code_arg)
    assert row is not None
    assert row.name == name
=== END AC acct-add-success ===

=== AC acct-add-duplicate ===
Intent: Adding a code that already exists exits 3 and leaves the stored name unchanged.

from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZAA2"
original = "Original Name"
with db_session() as db:
    db.accounts.create(account=code_arg, name=original)
    code, out, err = cli_runner("account", "add", code_arg, "Other Name")
    print(out, err)
    assert code == 3
    assert out == ""
    row = db.accounts.get(account=code_arg)
    assert row is not None
    assert row.name == original
=== END AC acct-add-duplicate ===

=== AC acct-add-invalid-code ===
Intent: Codes that are lowercase, too long, contain a symbol, or are empty are rejected with exit 3 and nothing is stored.

from cli.testing import cli_runner
from persistence.testing import db_session

bad_codes = ["zzlower", "Z" * 13, "ZZ-BAD", ""]
with db_session() as db:
    before = [r.account for r in db.accounts.list()]
    for bad in bad_codes:
        code, out, err = cli_runner("account", "add", bad, "Valid Name")
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
    after = [r.account for r in db.accounts.list()]
    assert after == before
=== END AC acct-add-invalid-code ===

=== AC acct-add-invalid-name ===
Intent: Names that are empty, longer than 40 characters, or contain a comma or newline are rejected with exit 3 and the account is not created.

from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZAA3"
bad_names = ["", "n" * 41, "has, comma", "has\nnewline"]
with db_session() as db:
    for bad in bad_names:
        code, out, err = cli_runner("account", "add", code_arg, bad)
        print(repr(bad), code, out, err)
        assert code == 3
        assert out == ""
        assert db.accounts.get(account=code_arg) is None
=== END AC acct-add-invalid-name ===

=== AC acct-add-boundaries ===
Intent: A 12-character code and a 40-character name are the accepted maxima and are stored exactly.

from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZ" + "B" * 10
name = "n" * 40
with db_session() as db:
    code, out, err = cli_runner("account", "add", code_arg, name)
    print(out, err)
    assert code == 0
    row = db.accounts.get(account=code_arg)
    assert row is not None
    assert row.name == name
=== END AC acct-add-boundaries ===

=== AC acct-add-usage ===
Intent: Wrong argument counts and an unknown verb are usage errors with exit 2 and create nothing.

from cli.testing import cli_runner
from persistence.testing import db_session

code_arg = "ZZAA4"
with db_session() as db:
    attempts = [
        ("account", "add"),
        ("account", "add", code_arg),
        ("account", "add", code_arg, "Name", "extra"),
        ("account", "frobnicate", code_arg),
    ]
    for args in attempts:
        code, out, err = cli_runner(*args)
        print(args, code, out, err)
        assert code == 2
        assert out == ""
    assert db.accounts.get(account=code_arg) is None
=== END AC acct-add-usage ===

## User Acceptance

- None.

## Guardrails

- A rejected add writes nothing.
- Balance is derived from stored transactions, never stored on the account.
- Only the generated persistence package touches the database.
