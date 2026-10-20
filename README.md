# LayersTesting

A Drydock UAT kit that exercises the language and persistence layers with a command-line cash
ledger. The brief is original to this kit.

| Path | Role |
|---|---|
| `sources/INSTRUCTIONS.md` | The specification imported into the Target. |
| `sources/seed_*.csv` | Known dataset: 4 accounts, 7 categories, 120 transactions; plus an 11-row file rejected on row 11. |
| `bin/run.sh` | The grader. Staged into the build as `sources/run.sh`; `acceptance.full` runs it. |
| `inputs/` | Frozen `SEA_TRIALS.md`, `TECHNOLOGY_STACK_python.md`, `TECHNOLOGY_STACK_go.md`, `COMPASS.md`, `METADATA.md`. |

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
| Z | re-`init` drops every row |

Exit `0` only when all 43 pass. The database is a temporary SQLite file unless `DATABASE_URL` is
set, so `DATABASE_URL=postgresql://... bin/run.sh APP` grades the same build against PostgreSQL.

## Variants

Two stack files carry the same exam. `uat.json` `technology_stack` selects one; the known answers
do not change with the stack.

| File | Stack |
|---|---|
| `inputs/TECHNOLOGY_STACK_python.md` | Python, SQLite, pytest (default) |
| `inputs/TECHNOLOGY_STACK_go.md` | Go, SQLite, go test |

For PostgreSQL, replace `sqlite.md` with `postgres.md` in either file. The Go file has no `CLI`
row because `cli.md` requires `python.md`.
