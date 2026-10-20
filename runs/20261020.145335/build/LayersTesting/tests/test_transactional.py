"""Command transaction: a command commits in full or changes nothing."""

import pytest

from cli.transactional import run_command
from persistence import PersistenceError
from persistence.testing import db_session


def test_successful_command_commits_its_write() -> None:
    with db_session() as db:
        def succeeding(store):
            store.accounts.create(account="CASH1", name="Float")

        run_command(db, succeeding)

        rows = db.accounts.list()
        assert len(rows) == 1
        assert rows[0].account == "CASH1"
        assert rows[0].name == "Float"


def test_command_return_value_is_returned() -> None:
    with db_session() as db:
        def succeeding(store):
            store.accounts.create(account="CASH1", name="Float")
            return "done"

        assert run_command(db, succeeding) == "done"


def test_failing_command_rolls_back_single_table_write() -> None:
    with db_session() as db:
        def failing(store):
            store.accounts.create(account="CASH1", name="Float")
            raise ValueError("rejected after write")

        with pytest.raises(ValueError, match="rejected after write"):
            run_command(db, failing)

        assert len(db.accounts.list()) == 0


def test_failing_command_rolls_back_every_table_written() -> None:
    with db_session() as db:
        def failing(store):
            store.accounts.create(account="CASH1", name="Float")
            store.categories.create(category="OPENING", description="Opening balance")
            raise ValueError("rejected after two writes")

        with pytest.raises(ValueError):
            run_command(db, failing)

        assert len(db.accounts.list()) == 0
        assert len(db.categories.list()) == 0


def test_original_exception_is_reraised_unchanged() -> None:
    with db_session() as db:
        error = ValueError("the very same instance")

        def failing(store):
            raise error

        with pytest.raises(ValueError) as caught:
            run_command(db, failing)

        assert caught.value is error


def test_persistence_error_inside_command_rolls_back_earlier_writes() -> None:
    with db_session() as db:
        db.accounts.create(account="CASH1", name="Float")

        def failing(store):
            store.categories.create(category="OPENING", description="Opening balance")
            # Duplicate primary key: the store refuses it, and the command must not survive.
            store.accounts.create(account="CASH1", name="Again")

        with pytest.raises(PersistenceError):
            run_command(db, failing)

        assert len(db.categories.list()) == 0
        assert [row.name for row in db.accounts.list()] == ["Float"]


def test_writes_inside_successful_command_are_visible_to_later_reads_in_command() -> None:
    with db_session() as db:
        def succeeding(store):
            store.accounts.create(account="CASH1", name="Float")
            return [row.account for row in store.accounts.list()]

        assert run_command(db, succeeding) == ["CASH1"]


def test_driver_connect_is_restored_after_success() -> None:
    with db_session() as db:
        run_command(db, lambda store: store.accounts.create(account="CASH1", name="Float"))

        assert "connect" not in vars(db.driver)


def test_driver_connect_is_restored_after_failure() -> None:
    with db_session() as db:
        def failing(store):
            raise ValueError("boom")

        with pytest.raises(ValueError):
            run_command(db, failing)

        assert "connect" not in vars(db.driver)
        # The store still works for the next command.
        run_command(db, lambda store: store.accounts.create(account="CASH1", name="Float"))
        assert len(db.accounts.list()) == 1


def test_command_with_no_writes_succeeds_and_changes_nothing() -> None:
    with db_session() as db:
        assert run_command(db, lambda store: store.accounts.list()) == []
        assert db.accounts.list() == []


def test_failed_command_leaves_prior_committed_rows_intact() -> None:
    with db_session() as db:
        run_command(db, lambda store: store.accounts.create(account="CASH1", name="Float"))

        def failing(store):
            store.accounts.update(account="CASH1", name="Renamed")
            raise ValueError("rejected")

        with pytest.raises(ValueError):
            run_command(db, failing)

        assert [(row.account, row.name) for row in db.accounts.list()] == [("CASH1", "Float")]
