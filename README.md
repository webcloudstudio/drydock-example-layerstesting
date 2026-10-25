# LayersTesting

A Drydock UAT kit that exercises the language and persistence layers with a command-line cash
ledger. The brief is original to this kit.

| Path | Role |
|---|---|
| `sources/INSTRUCTIONS.md` | The specification imported into the Target. |
| `sources/seed_*.csv` | Known dataset: 4 accounts, 7 categories, 120 transactions; plus an 11-row file rejected on row 11. |
| `bin/run.sh` | The grader. Staged into the build as `sources/run.sh`; `acceptance.full` runs it. |
| `inputs/` | Frozen `SEA_TRIALS.md`, `TECHNOLOGY_STACK.md`, `COMPASS.md`, `METADATA.md`, plus `_python` / `_go` versions. |

## Grading

`bin/run.sh [APP]` runs `APP/ledger` (default: the current directory) against a fresh database
and makes 43 checks of exit code and standard output:

| Group | Checks |
|---|---|
| A | `init`, empty `count` |
| B | load 4 + 7 + 120 rows, `count` |
| C | `report balances`, `categories`, `monthly` over the seed |
| D | rejected loads leave 120 rows |
| E | account add / duplicate / get / rename / not found / in use / delete |
| F | transaction post / get / amend / not found / bad category, amount, date / delete / id reuse |
| G | atomic transfer; transfer, post, amend, delete refused on a negative balance |
| H | the three reports after the changes |
| U | usage errors |
| Z | re-`init` clears ledger records |

Exit `0` only when all 43 pass. The database is a temporary SQLite file unless `DATABASE_URL` is
set, so `DATABASE_URL=postgresql://... bin/run.sh APP` grades the same build against PostgreSQL.

## Variants

`uat.json` reads the canonical files. Three of them have a `_python` and a `_go` version. Copy one
language's versions over the canonical files and commit; the exam and known answers do not change.

| Canonical file | Varies by |
|---|---|
| `inputs/TECHNOLOGY_STACK.md` | Language, test-runner rows |
| `inputs/METADATA.md` | `stack:` field, one sentence of `short_description` |
| `sources/INSTRUCTIONS.md` | `## Stack` section |

```sh
for f in inputs/TECHNOLOGY_STACK inputs/METADATA sources/INSTRUCTIONS; do cp "${f}_go.md" "$f.md"; done
```

The canonical files currently hold the Python versions. For PostgreSQL, replace `sqlite.md` with
`postgres.md` in the stack file and `SQLite` in the brief's `## Stack`. The Go stack has no `CLI`
row because `cli.md` requires `python.md`.

Analyze sees the brief, COMPASS, and METADATA's description but not `TECHNOLOGY_STACK.md` or
`uat.json`. Those three files never name a kit file the model cannot read.

## Project acceptance boundary

Sea Trials gate observable ledger workflows: loading and retaining records, reports before and
after changes, account and transaction operations, atomic rejection, non-negative balances,
transfers, and CLI results. The supplied grader remains a required end-to-end check alongside
these criteria. Initialization and reset are grader prerequisites, not standalone release gates;
no criterion requires schema replacement or tests the database engine. Build instructions retain
stack constraints and the application test-runner requirement.

Contract revisions apply to future runs. Existing runs and their checksummed evidence retain
the inputs and verdicts captured when they ran.
