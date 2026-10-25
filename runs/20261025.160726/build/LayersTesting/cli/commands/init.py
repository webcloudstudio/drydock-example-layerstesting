"""``ledger init``: return the three ledger tables to an empty state."""

from persistence import PersistenceError

from cli.config import APP_ROOT
from cli.context import open_store
from cli.registry import register

SCHEMA_FILE = APP_ROOT / "schema.sql"


def init(args: list[str]) -> None:
    """Make sure the tables exist, then empty them in foreign-key order. Writes nothing to stdout."""
    with open_store() as db:
        _ensure_tables(db)
        db.transactions.clear(min_id=0)
        db.accounts.clear(first_code="")
        db.categories.clear(first_code="")


def _ensure_tables(db) -> None:
    """Apply the generated, idempotent schema only when a table is missing."""
    try:
        db.accounts.list()
        db.categories.list()
        db.transactions.list()
    except PersistenceError:
        db.execute_script(SCHEMA_FILE.read_text(encoding="utf-8"))


register(("init",), init, (0, 0))
