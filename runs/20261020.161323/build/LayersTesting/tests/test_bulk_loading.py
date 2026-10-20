from pathlib import Path

from cli.testing import cli_runner


def test_accounts_load_and_report_rows(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    source = tmp_path / "accounts.csv"
    source.write_text("account,name\nCASH,Front Drawer\nSAFE,Store Safe\n", encoding="utf-8")

    assert cli_runner("init", environ=env)[0] == 0
    code, output, _ = cli_runner("load", "accounts", str(source), environ=env)

    assert code == 0
    assert output == "table,loaded\naccounts,2\n"
    assert cli_runner("count", environ=env)[1].splitlines()[1] == "accounts,2"


def test_categories_load_and_persist_rows(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    source = tmp_path / "categories.csv"
    source.write_text("category,description\nSALES,Sales receipts\n", encoding="utf-8")

    code, output, _ = cli_runner("load", "categories", str(source), environ=env)

    assert code == 0
    assert output == "table,loaded\ncategories,1\n"
    assert cli_runner("count", environ=env)[1].splitlines()[2] == "categories,1"


def test_invalid_batch_writes_nothing(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    source = tmp_path / "accounts.csv"
    source.write_text("account,name\nGOOD,Good\nGOOD,Duplicate\n", encoding="utf-8")

    code, output, _ = cli_runner("load", "accounts", str(source), environ=env)

    assert code == 3
    assert output == ""
    assert cli_runner("count", environ=env)[1].splitlines()[1] == "accounts,0"


def test_header_and_missing_file_fail_without_stdout(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    wrong = tmp_path / "wrong.csv"
    wrong.write_text("name,account\nDrawer,CASH\n", encoding="utf-8")

    wrong_code, wrong_out, _ = cli_runner("load", "accounts", str(wrong), environ=env)
    missing_code, missing_out, _ = cli_runner("load", "accounts", str(tmp_path / "none.csv"), environ=env)

    assert wrong_code == 3
    assert wrong_out == ""
    assert missing_code == 1
    assert missing_out == ""


def test_transactions_load_and_round_trip_count(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    accounts = tmp_path / "accounts.csv"
    categories = tmp_path / "categories.csv"
    transactions = tmp_path / "transactions.csv"
    accounts.write_text("account,name\nA,Account A\n", encoding="utf-8")
    categories.write_text("category,description\nC,Category C\n", encoding="utf-8")
    transactions.write_text(
        "txn_id,date,account,category,amount,memo\n"
        "1,2026-01-01,A,C,10.00,opening\n",
        encoding="utf-8",
    )

    assert cli_runner("load", "accounts", str(accounts), environ=env)[0] == 0
    assert cli_runner("load", "categories", str(categories), environ=env)[0] == 0
    code, output, _ = cli_runner("load", "transactions", str(transactions), environ=env)

    assert code == 0
    assert output == "table,loaded\ntransactions,1\n"
    assert cli_runner("count", environ=env)[1].splitlines()[3] == "transactions,1"


def test_transaction_batch_unknown_reference_is_atomic(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    accounts = tmp_path / "accounts.csv"
    categories = tmp_path / "categories.csv"
    transactions = tmp_path / "transactions.csv"
    accounts.write_text("account,name\nA,Account A\n", encoding="utf-8")
    categories.write_text("category,description\nC,Category C\n", encoding="utf-8")
    transactions.write_text(
        "txn_id,date,account,category,amount,memo\n"
        "1,2026-01-01,A,C,10.00,valid\n"
        "2,2026-01-01,NOSUCH,C,10.00,invalid\n",
        encoding="utf-8",
    )
    assert cli_runner("load", "accounts", str(accounts), environ=env)[0] == 0
    assert cli_runner("load", "categories", str(categories), environ=env)[0] == 0

    code, output, _ = cli_runner("load", "transactions", str(transactions), environ=env)

    assert code == 3
    assert output == ""
    assert cli_runner("count", environ=env)[1].splitlines()[3] == "transactions,0"


def test_transaction_batch_rejects_negative_result(tmp_path: Path) -> None:
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    accounts = tmp_path / "accounts.csv"
    categories = tmp_path / "categories.csv"
    transactions = tmp_path / "transactions.csv"
    accounts.write_text("account,name\nA,Account A\n", encoding="utf-8")
    categories.write_text("category,description\nC,Category C\n", encoding="utf-8")
    transactions.write_text(
        "txn_id,date,account,category,amount,memo\n"
        "1,2026-01-01,A,C,-1.00,overdraw\n",
        encoding="utf-8",
    )
    assert cli_runner("load", "accounts", str(accounts), environ=env)[0] == 0
    assert cli_runner("load", "categories", str(categories), environ=env)[0] == 0

    code, output, _ = cli_runner("load", "transactions", str(transactions), environ=env)

    assert code == 3
    assert output == ""
    assert cli_runner("count", environ=env)[1].splitlines()[3] == "transactions,0"
