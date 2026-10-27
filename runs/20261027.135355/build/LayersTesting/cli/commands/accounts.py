"""Account commands: ``ledger account add|get|rename|delete``."""

from cli.registry import Command
from ledger_core.accounts import account_row
from ledger_core.errors import NotFound, Rejected
from ledger_core.money import format_cents
from ledger_core.validation import validate_code, validate_name

ACCOUNT_HEADER = ["account", "name", "transactions", "balance"]
DELETED_HEADER = ["deleted"]


def _account_rows(db, code: str) -> list[list[str]]:
    """Return the header and the live row for ``code``; raise ``NotFound`` when it is absent."""
    row = account_row(db, code)
    if row is None:
        raise NotFound(f"account {code} does not exist")
    account, name, transactions, cents = row
    return [ACCOUNT_HEADER, [account, name, str(transactions), format_cents(cents)]]


def account_add(db, args: list[str]) -> list[list[str]]:
    """Validate, reject a duplicate code, insert the account, and print its row."""
    code = validate_code(args[0])
    name = validate_name(args[1])
    if db.accounts.get(account=code) is not None:
        raise Rejected(f"account {code} already exists")
    db.accounts.create(account=code, name=name)
    return _account_rows(db, code)


def account_get(db, args: list[str]) -> list[list[str]]:
    """Print the account's live row. Read-only; an absent code exits 4."""
    return _account_rows(db, args[0])


def account_rename(db, args: list[str]) -> list[list[str]]:
    """Validate the new name, then change only the name of an existing account and print its row."""
    code, name = args[0], validate_name(args[1])
    if db.accounts.get(account=code) is None:
        raise NotFound(f"account {code} does not exist")
    db.accounts.update(account=code, name=name)
    return _account_rows(db, code)


def account_delete(db, args: list[str]) -> list[list[str]]:
    """Remove an account that has no transactions. Existence and use are both checked first."""
    code = args[0]
    if db.accounts.get(account=code) is None:
        raise NotFound(f"account {code} does not exist")
    if db.transactions.list(account=code):
        raise Rejected(f"account {code} has transactions and cannot be deleted")
    db.accounts.delete(account=code)
    return [DELETED_HEADER, [code]]


COMMANDS = {
    ("account", "add"): Command(account_add, 2, 2),
    ("account", "get"): Command(account_get, 1, 1),
    ("account", "rename"): Command(account_rename, 2, 2),
    ("account", "delete"): Command(account_delete, 1, 1),
}
