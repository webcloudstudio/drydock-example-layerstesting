"""bin/test.sh contract: slice selector, exit status, and the temporary database it exports.

Each case runs the script in a child process. The child pytest collects a sentinel module that
exists only for the duration of the case, and selects it by a token no other test name contains,
so the outer suite is never re-run from inside itself.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNNER = PROJECT_ROOT / "bin" / "test.sh"
SENTINEL = PROJECT_ROOT / "tests" / "test_zqsentinel.py"

SENTINEL_SOURCE = '''\
import os
from pathlib import Path


def test_zqsentinel_ok():
    out = os.environ.get("ZQSENTINEL_OUT")
    if out:
        Path(out).write_text(os.environ["DATABASE_URL"], encoding="utf-8")


def test_zqsentinel_bad():
    assert False
'''


@pytest.fixture
def sentinel():
    SENTINEL.write_text(SENTINEL_SOURCE, encoding="utf-8")
    try:
        yield SENTINEL
    finally:
        SENTINEL.unlink(missing_ok=True)


def _run(selector, out=None, database_url="/nonexistent/user.db"):
    env = dict(os.environ, DATABASE_URL=database_url)
    if out is not None:
        env["ZQSENTINEL_OUT"] = str(out)
    args = ["sh", str(RUNNER)] + ([selector] if selector is not None else [])
    return subprocess.run(args, cwd=PROJECT_ROOT, env=env, capture_output=True, text=True)


def test_selector_runs_passing_match_and_exits_zero(sentinel):
    assert _run("zqsentinel_ok").returncode == 0


def test_selector_runs_failing_match_and_exits_nonzero(sentinel):
    assert _run("zqsentinel_bad").returncode != 0


def test_selector_matching_nothing_exits_nonzero(sentinel):
    assert _run("zqsentinel_nomatch").returncode != 0


def test_runner_exports_fresh_temporary_database_not_the_callers(sentinel, tmp_path):
    out = tmp_path / "seen_database_url.txt"
    result = _run("zqsentinel_ok", out=out, database_url="/nonexistent/user.db")
    assert result.returncode == 0
    seen = Path(out.read_text(encoding="utf-8"))
    assert seen != Path("/nonexistent/user.db")
    assert seen.name == "test.db"
    assert not seen.parent.exists(), "temporary database directory must be removed after the run"


def test_runner_is_valid_posix_sh():
    dash = shutil.which("dash")
    if dash is None:
        pytest.skip("dash not installed")
    assert subprocess.run([dash, "-n", str(RUNNER)], capture_output=True).returncode == 0
