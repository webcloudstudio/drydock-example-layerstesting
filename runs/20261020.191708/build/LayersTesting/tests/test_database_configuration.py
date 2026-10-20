import os
import tempfile

from cli.testing import cli_runner


def test_database_url_precedes_database_path_and_initializes_schema():
    with tempfile.TemporaryDirectory() as directory:
        url_database = os.path.join(directory, "configured.db")
        old_url = os.environ.get("DATABASE_URL")
        old_path = os.environ.get("DATABASE_PATH")
        try:
            os.environ["DATABASE_URL"] = url_database
            os.environ["DATABASE_PATH"] = os.path.join(directory, "fallback.db")
            code, stdout, stderr = cli_runner("init")
            assert code == 0
            assert stdout == ""
            assert stderr == ""
            assert os.path.exists(url_database)
            assert not os.path.exists(os.environ["DATABASE_PATH"])
        finally:
            if old_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = old_url
            if old_path is None:
                os.environ.pop("DATABASE_PATH", None)
            else:
                os.environ["DATABASE_PATH"] = old_path


def test_database_missing_tables_is_operational_failure_without_output():
    with tempfile.TemporaryDirectory() as directory:
        database_path = os.path.join(directory, "empty.db")
        old_url = os.environ.get("DATABASE_URL")
        old_path = os.environ.get("DATABASE_PATH")
        try:
            os.environ["DATABASE_URL"] = database_path
            os.environ.pop("DATABASE_PATH", None)
            code, stdout, stderr = cli_runner("count")
            assert code == 1
            assert stdout == ""
            assert stderr != ""
        finally:
            if old_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = old_url
            if old_path is None:
                os.environ.pop("DATABASE_PATH", None)
            else:
                os.environ["DATABASE_PATH"] = old_path
