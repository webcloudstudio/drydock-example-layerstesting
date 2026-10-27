"""Account rows: the stored account and the live figures the account commands report.

``account_row`` computes the transaction count and the integer-cent balance from the database on
every call, so neither figure is stored or embedded.
"""

from persistence import Database

AccountRow = tuple[str, str, int, int]


def account_row(db: Database, code: str) -> AccountRow | None:
    """Return ``(account, name, transactions, balance_cents)``, or ``None`` when the account is absent."""
    account = db.accounts.get(account=code)
    if account is None:
        return None
    posted = db.transactions.list(account=code)
    return (account.account, account.name, len(posted), sum(txn.amount for txn in posted))
