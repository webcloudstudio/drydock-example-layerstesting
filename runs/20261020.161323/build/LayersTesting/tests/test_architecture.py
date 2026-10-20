from pathlib import Path

from cli.testing import cli_runner


def test_init_and_count_are_public_cli_commands(tmp_path: Path):
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    init_code, init_out, init_err = cli_runner("init", environ=env)
    assert init_code == 0
    assert init_out == ""
    assert isinstance(init_err, str)

    count_code, count_out, count_err = cli_runner("count", environ=env)
    assert count_code == 0
    assert count_out == "table,rows\naccounts,0\ncategories,0\ntransactions,0\n"
    assert isinstance(count_err, str)


def test_unknown_command_is_usage_error_without_stdout(tmp_path: Path):
    code, out, err = cli_runner("unknown-command", environ={"DATABASE_PATH": str(tmp_path / "x.db")})
    assert code == 2
    assert out == ""
    assert isinstance(err, str)


def test_init_recreates_all_tables(tmp_path: Path):
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    assert cli_runner("init", environ=env)[0] == 0

    # The lifecycle story's public persistence operation can seed a row before reset.
    from persistence import open_database

    db = open_database(env["DATABASE_PATH"])
    try:
        db.accounts.create(account="TEMP1", name="Temporary")
    finally:
        db.close()

    code, out, err = cli_runner("init", environ=env)
    assert code == 0
    assert out == ""
    assert isinstance(err, str)
    assert cli_runner("count", environ=env)[1] == (
        "table,rows\naccounts,0\ncategories,0\ntransactions,0\n"
    )


def test_account_add_creates_an_account_for_lifecycle_reset(tmp_path: Path):
    env = {"DATABASE_PATH": str(tmp_path / "ledger.db")}
    assert cli_runner("init", environ=env)[0] == 0

    code, out, err = cli_runner("account", "add", "TEMP1", "Temporary", environ=env)

    assert code == 0
    assert out == ""
    assert isinstance(err, str)
    from persistence import open_database

    db = open_database(env["DATABASE_PATH"])
    try:
        assert db.accounts.get(account="TEMP1").name == "Temporary"
    finally:
        db.close()

