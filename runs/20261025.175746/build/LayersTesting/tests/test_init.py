"""``ledger init``: reset the ledger to empty, silently, with no DDL."""

from __future__ import annotations

from cli.testing import cli_runner


def _seed(db) -> None:
    db.accounts.create(account="UTINI1", name="Init Probe")
    db.categories.create(category="UTINIC1", description="Init Category")
    db.transactions.create(
        txn_id=970001, date="2026-04-01", account="UTINI1", category="UTINIC1", amount=500, memo="x"
    )


def test_init_removes_every_account_category_and_transaction(scratch_db):
    _seed(scratch_db)
    code, out, _ = cli_runner("init")
    assert code == 0
    assert out == ""
    assert scratch_db.transactions.list() == []
    assert scratch_db.categories.list() == []
    assert scratch_db.accounts.list() == []


def test_init_on_an_empty_ledger_still_exits_zero_and_stays_empty(scratch_db):
    first = cli_runner("init")
    second = cli_runner("init")
    assert first[0] == 0
    assert second[0] == 0
    assert second[1] == ""
    assert scratch_db.accounts.list() == []
    assert scratch_db.categories.list() == []
    assert scratch_db.transactions.list() == []


def test_init_twice_leaves_the_same_empty_ledger(scratch_db):
    _seed(scratch_db)
    cli_runner("init")
    cli_runner("init")
    assert scratch_db.accounts.list() == []


def test_init_writes_nothing_to_standard_error_on_success(scratch_db):
    _seed(scratch_db)
    code, _, err = cli_runner("init")
    assert code == 0
    assert err == ""


def test_init_with_an_extra_argument_is_a_usage_error_that_changes_nothing(scratch_db):
    scratch_db.accounts.create(account="UTINI2", name="Kept")
    code, out, _ = cli_runner("init", "extra")
    assert code == 2
    assert out == ""
    assert scratch_db.accounts.get(account="UTINI2") is not None


def test_init_keeps_the_schema_so_rows_can_be_added_again(scratch_db):
    _seed(scratch_db)
    cli_runner("init")
    scratch_db.accounts.create(account="UTINI3", name="Again")
    assert scratch_db.accounts.get(account="UTINI3").name == "Again"
