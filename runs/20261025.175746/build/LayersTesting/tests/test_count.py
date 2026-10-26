"""``ledger count``: read back through the CLI runner and the store, never from embedded values."""

from __future__ import annotations

import csv
import io

from cli.testing import cli_runner


def _counts(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def test_count_reports_header_and_stored_rows_in_declared_order(scratch_db):
    scratch_db.accounts.create(account="UTCNT1", name="Count Probe")
    scratch_db.categories.create(category="UTCNTC1", description="Count Category")
    scratch_db.transactions.create(
        txn_id=960001, date="2026-04-01", account="UTCNT1", category="UTCNTC1", amount=100, memo=""
    )
    code, out, _ = cli_runner("count")
    assert code == 0
    rows = _counts(out)
    assert rows[0] == ["table", "rows"]
    assert [row[0] for row in rows[1:]] == ["accounts", "categories", "transactions"]
    assert [int(row[1]) for row in rows[1:]] == [1, 1, 1]


def test_count_of_empty_store_is_zero_for_every_table(scratch_db):
    code, out, _ = cli_runner("count")
    assert code == 0
    assert [int(row[1]) for row in _counts(out)[1:]] == [0, 0, 0]


def test_count_tracks_rows_added_after_a_previous_count(scratch_db):
    def accounts_count() -> int:
        _, out, _ = cli_runner("count")
        return int(_counts(out)[1][1])

    before = accounts_count()
    scratch_db.accounts.create(account="UTCNT2A", name="One")
    scratch_db.accounts.create(account="UTCNT2B", name="Two")
    assert accounts_count() == before + 2


def test_count_writes_nothing_to_the_store(scratch_db):
    scratch_db.accounts.create(account="UTCNT4", name="Stable")
    cli_runner("count")
    assert [row.account for row in scratch_db.accounts.list()] == ["UTCNT4"]


def test_count_with_an_extra_argument_is_a_usage_error_with_no_stdout(scratch_db):
    code, out, _ = cli_runner("count", "extra")
    assert code == 2
    assert out == ""


def test_count_after_init_reports_zero_rows(scratch_db):
    scratch_db.accounts.create(account="UTCNT3", name="Gone")
    assert cli_runner("init")[0] == 0
    code, out, _ = cli_runner("count")
    assert code == 0
    assert [int(row[1]) for row in _counts(out)[1:]] == [0, 0, 0]
