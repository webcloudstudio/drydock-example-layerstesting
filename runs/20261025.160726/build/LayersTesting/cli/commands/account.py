"""``ledger account``: add, get, rename, and delete one account."""

from cli.context import open_store
from cli.core import validate_code, validate_name
from cli.errors import NotFound, Rejected
from cli.registry import register
from cli.views import ACCOUNT_HEADER, account_row


def add_account(args: list[str]) -> list[list[str]]:
    code, name = args
    validate_code(code)
    validate_name(name)
    with open_store() as db:
        if db.accounts.get(account=code) is not None:
            raise Rejected(f"account {code} already exists")
        created = db.accounts.create(account=code, name=name)
        return [ACCOUNT_HEADER, account_row(created, db.transactions.list(account=code))]


def get_account(args: list[str]) -> list[list[str]]:
    (code,) = args
    with open_store() as db:
        account = db.accounts.get(account=code)
        if account is None:
            raise NotFound(f"no account {code}")
        return [ACCOUNT_HEADER, account_row(account, db.transactions.list(account=code))]


def rename_account(args: list[str]) -> list[list[str]]:
    code, name = args
    validate_name(name)
    with open_store() as db:
        if db.accounts.get(account=code) is None:
            raise NotFound(f"no account {code}")
        renamed = db.accounts.update(account=code, name=name)
        return [ACCOUNT_HEADER, account_row(renamed, db.transactions.list(account=code))]


def delete_account(args: list[str]) -> list[list[str]]:
    (code,) = args
    with open_store() as db:
        if db.accounts.get(account=code) is None:
            raise NotFound(f"no account {code}")
        if db.transactions.list(account=code):
            raise Rejected(f"account {code} has transactions and cannot be deleted")
        db.accounts.delete(account=code)
    return [["deleted"], [code]]


register(("account", "add"), add_account, (2, 2))
register(("account", "get"), get_account, (1, 1))
register(("account", "rename"), rename_account, (2, 2))
register(("account", "delete"), delete_account, (1, 1))
