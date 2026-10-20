# COMPASS: LayersTesting

## Compass

Build a command-line cash ledger, an executable named `ledger` at the application root, as
described in `sources/INSTRUCTIONS.md`. It keeps accounts, categories, and cash transactions in a
relational database reached only through the shipped persistence library, rejects a failing command
before it writes, enforces non-negative balances, and reports balances, category totals, and monthly totals.

Correctness is measured by `sources/run.sh`: 43 checks of exit code and standard output against
known answers computed from the seed files. The goal is every check passing.

## Constraints

- Implement in the language and database named under `## Stack` in `sources/INSTRUCTIONS.md`.
- Provide an executable named `ledger` at the application root, invoked as `./ledger <command>`.
- Read the database location from `DATABASE_URL`, then `DATABASE_PATH`, then `data/app.db`.
- Store amounts as integer cents.
- Check every command in full before its first write.
- Run without network access other than to a PostgreSQL server named by `DATABASE_URL`.
- Diagnostics go to standard error and are never compared.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not read `sources/run.sh` or any seed file from application code. Seed files reach the
  database only through `ledger load`.
- Do not hardcode a report row, a count, or a total. Every value comes from a query.
- Do not open a database driver outside the shipped persistence library.
- Do not use floating point for money at any layer.

## Verification Protocol

| Story kind | Command | Asserts |
|---|---|---|
| Every behavioral story | `sh bin/test.sh` | exit `0` |
| Terminal story (once, last) | `sh sources/run.sh` | exit `0` |

<!-- drydock:build-write-guardrail:start -->
## Build Write Guardrail

- Authorized build directory: `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/build/LayersTesting`
- Authorized Target directory: `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting`
- Build agents have permission to create, modify, and remove files required by the active build block inside these authorized directories.
- No path outside these authorized directories may be modified.
- Protected Drydock artifacts:
  - `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/blueprint/`
  - `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/MANIFEST.md`
  - `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/COMPASS.md`
  - `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/QuarterDeck/`
  - `/mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261020.183046/workspace/targets/LayersTesting/evidence/`
<!-- drydock:build-write-guardrail:end -->
