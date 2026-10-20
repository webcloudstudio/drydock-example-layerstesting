"""Command transaction: one command, one transaction, committed on return and rolled back on failure.

Each test acts through ``run_command`` and reads the result back through the public ``db``
interface. Stores are fresh per test: a temporary SQLite store from ``db_session()``, or a file under
``tmp_path`` when a second connection must hold a lock.
"""

import sqlite3

import pytest

from persistence import PersistenceError, UnknownOperation
from persistence.testing import db_session
from transaction import run_command


class Abort(Exception):
    pass


def _seed(db) -> None:
    db.accounts.create(account="CASH", name="Cash on hand")
    db.categories.create(category="FOOD", description="Groceries")


def _account_codes(db) -> set[str]:
    return {row.account for row in db.accounts.list()}


# --- commit on return -----------------------------------------------------------------


def test_committed_write_is_visible_to_a_separate_connection(tmp_path):
    path = str(tmp_path / "ledger.db")
    with db_session(path) as db:
        run_command(db, lambda d: d.accounts.create(account="DURA", name="Durable"))
        reader = sqlite3.connect(path)
        try:
            names = reader.execute("SELECT name FROM accounts WHERE account = 'DURA'").fetchall()
        finally:
            reader.close()
        assert names == [("Durable",)]


def test_rolled_back_write_is_absent_from_a_separate_connection(tmp_path):
    path = str(tmp_path / "ledger.db")

    def write_then_fail(d):
        d.accounts.create(account="GONE", name="Never committed")
        raise Abort()

    with db_session(path) as db:
        with pytest.raises(Abort):
            run_command(db, write_then_fail)
        reader = sqlite3.connect(path)
        try:
            rows = reader.execute("SELECT account FROM accounts WHERE account = 'GONE'").fetchall()
        finally:
            reader.close()
        assert rows == []


def test_command_write_is_persisted_after_run_command_returns():
    with db_session() as db:
        run_command(db, lambda d: d.accounts.create(account="TXNA1", name="Commit Test"))
        assert db.accounts.get(account="TXNA1").name == "Commit Test"


def test_run_command_returns_the_value_the_command_returned():
    with db_session() as db:
        sentinel = object()
        assert run_command(db, lambda d: sentinel) is sentinel


def test_run_command_returns_none_when_the_command_returns_none():
    with db_session() as db:
        assert run_command(db, lambda d: None) is None


def test_a_read_only_command_returns_its_value_and_changes_nothing():
    with db_session() as db:
        _seed(db)
        codes = run_command(db, lambda d: sorted(row.account for row in d.accounts.list()))
        assert codes == ["CASH"]
        assert _account_codes(db) == {"CASH"}


def test_command_sees_its_own_uncommitted_writes():
    with db_session() as db:
        seen = run_command(
            db,
            lambda d: (
                d.accounts.create(account="TXNS1", name="Visible"),
                d.accounts.get(account="TXNS1").name,
            )[1],
        )
        assert seen == "Visible"


def test_commands_on_one_store_each_commit_independently():
    with db_session() as db:
        run_command(db, lambda d: d.accounts.create(account="FIRST", name="One"))
        run_command(db, lambda d: d.accounts.create(account="SECOND", name="Two"))
        assert _account_codes(db) == {"FIRST", "SECOND"}


# --- the declared acceptance assertions, as tests --------------------------------------


def test_committed_command_persists_exactly_one_matching_row():
    with db_session() as db:
        run_command(db, lambda d: d.accounts.create(account="TXNA1", name="Commit Test"))
        matches = [row for row in db.accounts.list() if row.account == "TXNA1"]
        assert len(matches) == 1
        assert matches[0].name == "Commit Test"


def test_failure_after_two_writes_leaves_neither_write_and_reraises_the_exception():
    first_code = "TXNB1"
    second_code = "TXNB2"

    def write_then_fail(d):
        d.accounts.create(account=first_code, name="Rollback First")
        d.accounts.create(account=second_code, name="Rollback Second")
        raise Abort("forced after two writes")

    with db_session() as db:
        before = len(db.accounts.list())
        with pytest.raises(Abort):
            run_command(db, write_then_fail)
        after = db.accounts.list()
        assert len(after) == before
        assert all(row.account not in (first_code, second_code) for row in after)


def test_exception_from_a_failing_command_is_the_same_object_the_caller_receives():
    raised_error = RuntimeError("forced by test")

    def fail(d):
        raise raised_error

    with db_session() as db:
        with pytest.raises(RuntimeError) as caught:
            run_command(db, fail)
        assert caught.value is raised_error


# --- rollback covers every kind of write ----------------------------------------------


def test_failure_rolls_back_an_update_made_earlier_in_the_command():
    def rename_then_fail(d):
        d.accounts.update(account="CASH", name="Renamed")
        raise Abort()

    with db_session() as db:
        _seed(db)
        with pytest.raises(Abort):
            run_command(db, rename_then_fail)
        assert db.accounts.get(account="CASH").name == "Cash on hand"


def test_failure_rolls_back_a_delete_made_earlier_in_the_command():
    def delete_then_fail(d):
        d.accounts.delete(account="CASH")
        raise Abort()

    with db_session() as db:
        _seed(db)
        with pytest.raises(Abort):
            run_command(db, delete_then_fail)
        assert db.accounts.get(account="CASH") is not None


def test_failure_rolls_back_writes_across_different_tables():
    def write_both_then_fail(d):
        d.accounts.create(account="MIXA", name="Mixed")
        d.categories.create(category="MIXC", description="Mixed")
        raise Abort()

    with db_session() as db:
        with pytest.raises(Abort):
            run_command(db, write_both_then_fail)
        assert db.accounts.get(account="MIXA") is None
        assert db.categories.get(category="MIXC") is None


def test_persistence_error_mid_command_rolls_back_the_earlier_write():
    def duplicate_key_after_a_write(d):
        d.accounts.create(account="NEW1", name="Before the error")
        d.accounts.create(account="CASH", name="Duplicate primary key")

    with db_session() as db:
        _seed(db)
        with pytest.raises(PersistenceError):
            run_command(db, duplicate_key_after_a_write)
        assert db.accounts.get(account="NEW1") is None
        assert db.accounts.get(account="CASH").name == "Cash on hand"


def test_undeclared_operation_inside_a_command_raises_and_rolls_back():
    def write_then_misuse(d):
        d.accounts.create(account="MISU", name="Before misuse")
        d.accounts.purge(account="MISU")

    with db_session() as db:
        with pytest.raises(UnknownOperation):
            run_command(db, write_then_misuse)
        assert db.accounts.get(account="MISU") is None


def test_failed_command_leaves_the_store_usable_for_the_next_command():
    def write_then_fail(d):
        d.accounts.create(account="AGAIN", name="First try")
        raise Abort()

    with db_session() as db:
        with pytest.raises(Abort):
            run_command(db, write_then_fail)
        run_command(db, lambda d: d.accounts.create(account="AGAIN", name="Second try"))
        assert db.accounts.get(account="AGAIN").name == "Second try"


# --- write lock held by another connection --------------------------------------------


def test_write_lock_held_by_another_connection_raises_and_changes_nothing(tmp_path):
    path = str(tmp_path / "ledger.db")
    with db_session(path) as db:
        _seed(db)
        db.driver.connect().execute("PRAGMA busy_timeout=50")
        holder = sqlite3.connect(path, timeout=0)
        try:
            holder.execute("BEGIN IMMEDIATE")
            holder.execute(
                "INSERT INTO accounts (account, name) VALUES ('HELD', 'Held elsewhere')"
            )
            with pytest.raises(PersistenceError):
                run_command(db, lambda d: d.accounts.create(account="LOCK", name="Blocked"))
            holder.rollback()
        finally:
            holder.close()
        assert db.accounts.get(account="LOCK") is None
        assert _account_codes(db) == {"CASH"}
