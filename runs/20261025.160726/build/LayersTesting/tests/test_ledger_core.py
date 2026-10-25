"""Ledger core: amount parsing and formatting, field and date validators, and the projected-balance guard.

Each acceptance assertion from FEATURE-LedgerCore.md has a test here. The guard tests run inside the
shared rollback session, so nothing they create persists in the application store.
"""

from pathlib import Path

import pytest

from cli.core import (
    account_balance,
    balance_guard,
    format_amount,
    parse_amount,
    validate_code,
    validate_date,
    validate_memo,
    validate_name,
)
from cli.errors import Rejected
from persistence.testing import db_session

APP_ROOT = Path(__file__).resolve().parent.parent


def _rejects(fn, text) -> bool:
    try:
        fn(text)
    except Rejected:
        return True
    return False


# parse_amount

def test_parse_amount_reads_decimal_text_as_integer_cents():
    assert parse_amount("12.50") == 1250
    assert parse_amount("-12.50") == -1250
    assert parse_amount("5") == 500
    assert parse_amount("7.5") == 750
    assert parse_amount("0.01") == 1
    assert parse_amount("5000.00") == 500000


def test_parse_amount_returns_an_int():
    assert isinstance(parse_amount("1.25"), int)


@pytest.mark.parametrize("text", ["0", "0.00", "-0.0"])
def test_parse_amount_rejects_zero(text):
    assert _rejects(parse_amount, text)


@pytest.mark.parametrize("text", ["1.234", "", ".5", "1.", "abc", "+1.00", "1,000.00", "1 .00", "--1"])
def test_parse_amount_rejects_excess_decimals_and_malformed_text(text):
    assert _rejects(parse_amount, text)


def test_parse_amount_accepts_one_and_two_decimals_at_the_boundaries():
    assert parse_amount("-0.01") == -1
    assert parse_amount("-5") == -500


def test_parse_amount_rejects_non_ascii_digits():
    assert _rejects(parse_amount, "١.00")


# format_amount

def test_format_amount_prints_negative_with_leading_minus():
    assert format_amount(-1250) == "-12.50"


def test_format_amount_prints_zero_with_two_decimals():
    assert format_amount(0) == "0.00"


def test_format_amount_prints_whole_amount_with_two_decimals():
    assert format_amount(500000) == "5000.00"


def test_format_amount_pads_a_single_cent_digit():
    assert format_amount(5) == "0.05"


def test_format_amount_has_no_thousands_separator():
    assert "," not in format_amount(123456789)


@pytest.mark.parametrize("cents", [1, -1, 99, 100, -100, 123456, -987654, 500000])
def test_format_amount_round_trips_through_parse_amount(cents):
    assert parse_amount(format_amount(cents)) == cents


# validate_code

def test_validate_code_accepts_twelve_characters():
    good = "A" * 12
    assert validate_code(good) == good


def test_validate_code_accepts_letters_and_digits():
    assert validate_code("DRAWER1") == "DRAWER1"


@pytest.mark.parametrize("text", ["", "A" * 13, "drawer", "AB-C", "A B", "A,B", "ÅB"])
def test_validate_code_rejects_out_of_set_or_out_of_bounds(text):
    assert _rejects(validate_code, text)


# validate_name and validate_memo

def test_validate_name_accepts_forty_characters():
    name = "n" * 40
    assert validate_name(name) == name


def test_validate_name_rejects_empty_and_forty_one_characters():
    assert _rejects(validate_name, "")
    assert _rejects(validate_name, "n" * 41)


def test_validate_memo_accepts_sixty_characters_and_empty():
    memo = "m" * 60
    assert validate_memo(memo) == memo
    assert validate_memo("") == ""


def test_validate_memo_rejects_sixty_one_characters():
    assert _rejects(validate_memo, "m" * 61)


@pytest.mark.parametrize("bad", ["a,b", "a\nb", "a\rb"])
def test_validate_name_rejects_comma_and_line_breaks(bad):
    assert _rejects(validate_name, bad)


@pytest.mark.parametrize("bad", ["a,b", "a\nb", "a\rb"])
def test_validate_memo_rejects_comma_and_line_breaks(bad):
    assert _rejects(validate_memo, bad)


# validate_date

@pytest.mark.parametrize("good", ["2026-04-01", "2028-02-29", "2026-12-31"])
def test_validate_date_accepts_real_calendar_dates(good):
    assert validate_date(good) == good


@pytest.mark.parametrize(
    "bad",
    ["2026-02-30", "2026-13-01", "2027-02-29", "2026-4-1", "20260401", "2026/04/01", "", "2026-04-01x"],
)
def test_validate_date_rejects_impossible_or_malformed_dates(bad):
    assert _rejects(validate_date, bad)


def test_validate_date_rejects_year_zero():
    assert _rejects(validate_date, "0000-01-01")


# Source scan: the core module must not use floating point.

def test_core_module_has_no_float_literal_or_float_conversion():
    import ast

    with open(APP_ROOT / "cli" / "core.py", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    float_literals = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    float_names = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "float"]
    assert float_literals == []
    assert float_names == []


# account_balance and balance_guard

def test_guard_accepts_change_that_keeps_balance_non_negative_and_writes_nothing():
    with db_session() as db:
        acct = "ACPTBG1"
        cat = "ACPTBGC"
        db.accounts.create(account=acct, name="Guard Account")
        db.categories.create(category=cat, description="Guard Category")
        new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
        funded = 1000
        db.transactions.create(
            txn_id=new_id, date="2026-06-01", account=acct, category=cat, amount=funded, memo=""
        )
        rows_before = len(db.transactions.list(account=acct))
        assert account_balance(db, acct) == funded

        balance_guard(db, {acct: -funded})

        with pytest.raises(Rejected):
            balance_guard(db, {acct: -funded - 1})
        assert len(db.transactions.list(account=acct)) == rows_before
        assert account_balance(db, acct) == funded


def test_guard_rejects_when_any_one_account_would_go_negative():
    with db_session() as db:
        rich = "ACPTBM1"
        poor = "ACPTBM2"
        cat = "ACPTBMC"
        db.accounts.create(account=rich, name="Rich")
        db.accounts.create(account=poor, name="Poor")
        db.categories.create(category=cat, description="Multi")
        new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
        db.transactions.create(
            txn_id=new_id, date="2026-06-02", account=rich, category=cat, amount=5000, memo=""
        )
        balance_guard(db, {rich: -5000, poor: 5000})

        with pytest.raises(Rejected):
            balance_guard(db, {rich: 100, poor: -1})


def test_account_balance_is_zero_for_an_account_with_no_transactions():
    with db_session() as db:
        db.accounts.create(account="ACPTBZ1", name="Empty")
        assert account_balance(db, "ACPTBZ1") == 0


def test_guard_accepts_a_change_that_lands_exactly_on_zero():
    with db_session() as db:
        acct = "ACPTBE1"
        cat = "ACPTBEC"
        db.accounts.create(account=acct, name="Exact")
        db.categories.create(category=cat, description="Exact")
        new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
        db.transactions.create(
            txn_id=new_id, date="2026-06-03", account=acct, category=cat, amount=250, memo=""
        )
        balance_guard(db, {acct: -250})


def test_guard_accepts_an_empty_change_set():
    with db_session() as db:
        balance_guard(db, {})


def test_guard_rejects_an_account_with_no_funds_for_any_debit():
    with db_session() as db:
        acct = "ACPTBN1"
        db.accounts.create(account=acct, name="No Funds")
        with pytest.raises(Rejected):
            balance_guard(db, {acct: -1})


def test_guard_checks_each_account_against_its_own_balance():
    with db_session() as db:
        first = "ACPTBS1"
        second = "ACPTBS2"
        cat = "ACPTBSC"
        db.accounts.create(account=first, name="First")
        db.accounts.create(account=second, name="Second")
        db.categories.create(category=cat, description="Separate")
        new_id = max([t.txn_id for t in db.transactions.list()], default=0) + 1
        db.transactions.create(
            txn_id=new_id, date="2026-06-04", account=first, category=cat, amount=100, memo=""
        )
        with pytest.raises(Rejected):
            balance_guard(db, {first: -50, second: -1})
