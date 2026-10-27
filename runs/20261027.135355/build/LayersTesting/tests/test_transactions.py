"""``ledger txn post``, ``txn_row``, and ``next_txn_id``, against a fresh store per test."""

import csv
import io

import pytest

from cli.testing import cli_runner
from ledger_core.transactions import next_txn_id, txn_row
from persistence.schema import TransactionsGetOutput

TXN_HEADER = ["txn_id", "date", "account", "category", "amount", "memo"]
ACCOUNT = "ZZTA1"
CATEGORY = "ZZTC1"


@pytest.fixture
def posting_store(ledger_store, store_open):
    """A store with one account and one category, ready for postings."""
    with store_open(ledger_store) as db:
        db.accounts.create(account=ACCOUNT, name="Post Probe")
        db.categories.create(category=CATEGORY, description="Post Category")
    return ledger_store


def _rows(out: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(out)))


def _stored(store_open, path):
    with store_open(path) as db:
        return db.transactions.list()


def test_post_prints_header_and_new_row(posting_store, store_open):
    code, out, err = cli_runner("txn", "post", ACCOUNT, CATEGORY, "45.50", "2026-04-01", "walk in sale")
    assert code == 0, err
    assert _rows(out) == [TXN_HEADER, ["1", "2026-04-01", ACCOUNT, CATEGORY, "45.50", "walk in sale"]]


def test_posted_row_reads_back_with_cent_amount_and_memo(posting_store, store_open):
    cli_runner("txn", "post", ACCOUNT, CATEGORY, "45.50", "2026-04-01", "walk in sale")
    with store_open(posting_store) as db:
        stored = db.transactions.get(txn_id=1)
    assert stored.amount == 4550
    assert stored.memo == "walk in sale"
    assert stored.date == "2026-04-01"


def test_omitted_memo_is_stored_empty_and_prints_six_fields(posting_store, store_open):
    code, out, err = cli_runner("txn", "post", ACCOUNT, CATEGORY, "10.00", "2026-04-02")
    assert code == 0, err
    assert _rows(out)[1] == ["1", "2026-04-02", ACCOUNT, CATEGORY, "10.00", ""]
    with store_open(posting_store) as db:
        assert db.transactions.get(txn_id=1).memo == ""


def test_consecutive_posts_get_consecutive_ids(posting_store):
    ids = []
    for amount in ["5.00", "6.00", "7.00"]:
        code, out, err = cli_runner("txn", "post", ACCOUNT, CATEGORY, amount, "2026-04-03")
        assert code == 0, err
        ids.append(int(_rows(out)[1][0]))
    assert ids == [1, 2, 3]


def test_next_id_follows_the_largest_stored_id_not_the_count(posting_store, store_open):
    with store_open(posting_store) as db:
        db.transactions.create(txn_id=500, date="2026-04-01", account=ACCOUNT, category=CATEGORY,
                               amount=100, memo="")
    code, out, err = cli_runner("txn", "post", ACCOUNT, CATEGORY, "1.00", "2026-04-02")
    assert code == 0, err
    assert _rows(out)[1][0] == "501"


@pytest.mark.parametrize(
    "case",
    [
        (ACCOUNT, "ZZNOCAT", "1.00", "2026-04-01"),
        ("ZZNOACCT", CATEGORY, "1.00", "2026-04-01"),
        (ACCOUNT, CATEGORY, "1.234", "2026-04-01"),
        (ACCOUNT, CATEGORY, "0", "2026-04-01"),
        (ACCOUNT, CATEGORY, "0.00", "2026-04-01"),
        (ACCOUNT, CATEGORY, "1.00", "2026-02-30"),
        (ACCOUNT, CATEGORY, "1.00", "2026-13-01"),
        (ACCOUNT, CATEGORY, "1.00", "04/01/2026"),
        (ACCOUNT, CATEGORY, "1.00", "2026-04-01", "bad,memo"),
        (ACCOUNT, CATEGORY, "1.00", "2026-04-01", "x" * 61),
        (ACCOUNT, CATEGORY, "abc", "2026-04-01"),
    ],
)
def test_rejections_exit_three_with_no_output_and_no_write(posting_store, store_open, case):
    before = len(_stored(store_open, posting_store))
    code, out, _ = cli_runner("txn", "post", *case)
    assert code == 3
    assert out == ""
    assert len(_stored(store_open, posting_store)) == before


def test_withdrawal_beyond_balance_is_rejected(posting_store, store_open):
    with store_open(posting_store) as db:
        db.transactions.create(txn_id=900001501, date="2026-04-01", account=ACCOUNT,
                               category=CATEGORY, amount=1000, memo="")
    before = len(_stored(store_open, posting_store))
    code, out, _ = cli_runner("txn", "post", ACCOUNT, CATEGORY, "-10.01", "2026-04-02")
    assert code == 3
    assert out == ""
    assert len(_stored(store_open, posting_store)) == before


def test_withdrawal_to_exactly_zero_is_accepted(posting_store, store_open):
    with store_open(posting_store) as db:
        db.transactions.create(txn_id=900001501, date="2026-04-01", account=ACCOUNT,
                               category=CATEGORY, amount=1000, memo="")
    code, out, err = cli_runner("txn", "post", ACCOUNT, CATEGORY, "-10.00", "2026-04-02")
    assert code == 0, err
    assert len(_stored(store_open, posting_store)) == 2


def test_balance_rule_counts_prior_postings(posting_store, store_open):
    assert cli_runner("txn", "post", ACCOUNT, CATEGORY, "5.00", "2026-04-01")[0] == 0
    assert cli_runner("txn", "post", ACCOUNT, CATEGORY, "-3.00", "2026-04-02")[0] == 0
    code, out, _ = cli_runner("txn", "post", ACCOUNT, CATEGORY, "-2.01", "2026-04-03")
    assert code == 3
    assert out == ""
    assert len(_stored(store_open, posting_store)) == 2


@pytest.mark.parametrize(
    "args",
    [
        ("txn", "post", ACCOUNT, CATEGORY, "1.00"),
        ("txn", "post", "A", "B", "1.00", "2026-04-01", "m", "extra"),
    ],
)
def test_wrong_argument_count_is_usage_error(posting_store, args):
    code, out, _ = cli_runner(*args)
    assert code == 2
    assert out == ""


def test_txn_row_formats_stored_fields(posting_store):
    txn = TransactionsGetOutput(txn_id=7, date="2026-06-01", account=ACCOUNT, category=CATEGORY,
                                amount=-1205, memo="rent")
    assert txn_row(txn) == ["7", "2026-06-01", ACCOUNT, CATEGORY, "-12.05", "rent"]


def test_next_txn_id_is_one_on_empty_ledger(ledger_store, store_open):
    with store_open(ledger_store) as db:
        assert next_txn_id(db) == 1


def test_next_txn_id_is_largest_plus_one(posting_store, store_open):
    with store_open(posting_store) as db:
        for txn_id in (3, 11, 7):
            db.transactions.create(txn_id=txn_id, date="2026-04-01", account=ACCOUNT,
                                   category=CATEGORY, amount=1, memo="")
        assert next_txn_id(db) == 12
