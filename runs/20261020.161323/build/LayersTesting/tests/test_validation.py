from pathlib import Path

from cli.testing import cli_runner
from validation import ValidationError, amount_cents, code, ledger_date, memo, name


def test_amount_parser_preserves_integer_cents_and_rejects_precision() -> None:
    assert amount_cents("12") == 1200
    assert amount_cents("-0.05") == -5
    for value in ("0", "1.234", "1.", "x"):
        try:
            amount_cents(value)
        except ValidationError:
            pass
        else:
            raise AssertionError(value)


def test_date_and_text_boundaries() -> None:
    assert ledger_date("2026-02-28") == "2026-02-28"
    assert memo() == ""
    assert name("A") == "A"
    for invalid in ("2026-02-30", "2026/02/01"):
        try:
            ledger_date(invalid)
        except ValidationError:
            pass
        else:
            raise AssertionError(invalid)
    for invalid in ("lower", "A-1", ""):
        try:
            code(invalid)
        except ValidationError:
            pass
        else:
            raise AssertionError(invalid)


def test_rejected_transaction_does_not_change_count(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    assert cli_runner("init", environ=env)[0] == 0
    assert cli_runner("account", "add", "VALID1", "Valid Account", environ=env)[0] == 0
    before = cli_runner("count", environ=env)[1]

    result, out, _ = cli_runner(
        "txn", "post", "VALID1", "UNKNOWN1", "1.00", "2026-01-01", environ=env
    )

    assert result == 3
    assert out == ""
    assert cli_runner("count", environ=env)[1] == before


def test_declared_transaction_rejections_return_status_three(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    assert cli_runner("init", environ=env)[0] == 0
    assert cli_runner("account", "add", "VALID1", "Valid Account", environ=env)[0] == 0
    for amount, transaction_date in (("1.234", "2026-01-01"), ("1.00", "2026-02-30"), ("-1.00", "2026-01-01")):
        result, out, _ = cli_runner(
            "txn", "post", "VALID1", "SALES", amount, transaction_date, environ=env
        )
        assert result == 3
        assert out == ""
