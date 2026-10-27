"""``run_all`` undo behaviour and ``parse_txn_id`` acceptance, tested without a database."""

import pytest

from ledger_core.atomic import run_all
from ledger_core.errors import Operational, Rejected
from ledger_core.transactions import parse_txn_id
from persistence import PersistenceError


def test_run_all_runs_every_insert_in_order_and_undoes_nothing():
    log = []
    run_all([(lambda: log.append("a"), lambda: log.append("undo a")), (lambda: log.append("b"), lambda: log.append("undo b"))])
    assert log == ["a", "b"]


def test_run_all_on_failure_undoes_completed_steps_newest_first():
    log = []

    def fail():
        raise PersistenceError("boom")

    steps = [
        (lambda: log.append("a"), lambda: log.append("undo a")),
        (lambda: log.append("b"), lambda: log.append("undo b")),
        (fail, lambda: log.append("undo c")),
    ]
    with pytest.raises(Operational):
        run_all(steps)
    assert log == ["a", "b", "undo b", "undo a"]


def test_run_all_does_not_undo_the_step_that_failed():
    log = []

    def fail():
        raise PersistenceError("boom")

    with pytest.raises(Operational):
        run_all([(fail, lambda: log.append("undo failed step"))])
    assert log == []


@pytest.mark.parametrize("text", ["1", "42", "-7", "900200001"])
def test_parse_txn_id_accepts_integers(text):
    assert parse_txn_id(text) == int(text)


@pytest.mark.parametrize("text", ["", "abc", "1.5", " 3", "3 ", "1e3", "--2", "+4"])
def test_parse_txn_id_rejects_non_integers(text):
    with pytest.raises(Rejected):
        parse_txn_id(text)
