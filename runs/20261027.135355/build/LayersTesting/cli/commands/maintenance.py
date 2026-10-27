"""Maintenance commands: ``ledger init`` empties the ledger, ``ledger count`` reports table row counts."""

from pathlib import Path

from cli.registry import Command
from ledger_core.config import database_path
from persistence import PersistenceError, open_database
from persistence import db as persistence_db

SCHEMA_SQL = Path(__file__).resolve().parents[2] / "schema.sql"


def _ensure_schema() -> None:
    """Create the declared tables when the configured store has none. A provisioned store is left alone.

    This runs on its own connection, before the command's connection first reads. Inside the
    acceptance harness the command's connection is joined to the harness transaction, which forbids
    schema SQL and would keep a pre-schema snapshot, so the harness is detached only while the
    standalone connection is opened. Nothing is written when the tables already exist.
    """
    harness = persistence_db._harness
    persistence_db._harness = None
    try:
        bootstrap = open_database(database_path())
    finally:
        persistence_db._harness = harness
    try:
        try:
            bootstrap.transactions.list()
        except PersistenceError:
            bootstrap.execute_script(SCHEMA_SQL.read_text(encoding="utf-8"))
    finally:
        bootstrap.close()


def init(db, args: list[str]) -> list[list[str]]:
    """Remove every transaction, then category, then account, in foreign-key order. Prints nothing."""
    _ensure_schema()
    db.transactions.clear(min_txn_id=0)
    db.categories.clear(min_category="")
    db.accounts.clear(min_account="")
    return []


def count(db, args: list[str]) -> list[list[str]]:
    """Report the stored row count of each table, read from the database on every run."""
    return [
        ["table", "rows"],
        ["accounts", str(len(db.accounts.list()))],
        ["categories", str(len(db.categories.list()))],
        ["transactions", str(len(db.transactions.list()))],
    ]


COMMANDS = {
    ("init",): Command(init, 0, 0),
    ("count",): Command(count, 0, 0),
}
