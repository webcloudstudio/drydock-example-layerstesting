# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-27
- resulting state: closed/verified
- story points (combined assembled cost): 23673
- execution id: -

## Stories built
- Declare the accounts, categories, and transactions tables and every repository operation the stories need. (foundation-database) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 1134)
- implements: DATABASE.md (SP 9825)
- stack: common_compact.md (SP 1653)
- stack: persistence.md (SP 6507)
- stack: sqlite.md (SP 3364)

## Pre-build acceptance observation
- RED: accounts-create (DATABASE.md)
  intent: accounts.create stores a row and returns the declared Output, which a separate get reads back.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-get (DATABASE.md)
  intent: accounts.get returns the stored row for an existing code and None for an absent one.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-update (DATABASE.md)
  intent: accounts.update changes only the name and the change is visible on a separate read.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the row so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-list (DATABASE.md)
  intent: accounts.list returns rows ordered by account code ascending; two codes created in reverse order appear in sorted order.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: accounts-clear (DATABASE.md)
  intent: accounts.clear removes accounts whose code is at or above the bound, reports a positive count, and leaves none readable.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-create (DATABASE.md)
  intent: categories.create stores a row and returns the declared Output, which a separate get reads back.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-get (DATABASE.md)
  intent: categories.get returns the stored row for an existing code and None for an absent one.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-update (DATABASE.md)
  intent: categories.update changes the description and the change is visible on a separate read.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-delete (DATABASE.md)
  intent: categories.delete removes the row so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-list (DATABASE.md)
  intent: categories.list returns rows ordered by category code ascending; two codes created in reverse order appear in sorted order.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: categories-clear (DATABASE.md)
  intent: categories.clear removes categories whose code is at or above the bound, reports a positive count, and leaves none readable.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-create (DATABASE.md)
  intent: transactions.create stores a signed integer-cents row under the supplied id and returns it, and a separate get reads every column back.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-get (DATABASE.md)
  intent: transactions.get returns the stored row for an existing id and None for an absent id.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and the change is visible on a separate read.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-list (DATABASE.md)
  intent: transactions.list filters by account and inclusive date range and returns rows by txn_id ascending; rows outside the range or on another account are excluded.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.
- RED: transactions-clear (DATABASE.md)
  intent: transactions.clear removes transactions at or above the bound, reports a positive count, and leaves none readable.
  error: foundation not built: `persistence` is the package the database foundation (postgres.md, sqlite.md) builds, and the build directory has no `persistence/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: accounts-create (DATABASE.md)
  intent: accounts.create stores a row and returns the declared Output, which a separate get reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: accounts-get (DATABASE.md)
  intent: accounts.get returns the stored row for an existing code and None for an absent one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: accounts-update (DATABASE.md)
  intent: accounts.update changes only the name and the change is visible on a separate read.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: accounts-delete (DATABASE.md)
  intent: accounts.delete removes the row so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: accounts-list (DATABASE.md)
  intent: accounts.list returns rows ordered by account code ascending; two codes created in reverse order appear in sorted order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: accounts-clear (DATABASE.md)
  intent: accounts.clear removes accounts whose code is at or above the bound, reports a positive count, and leaves none readable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-create (DATABASE.md)
  intent: categories.create stores a row and returns the declared Output, which a separate get reads back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-get (DATABASE.md)
  intent: categories.get returns the stored row for an existing code and None for an absent one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-update (DATABASE.md)
  intent: categories.update changes the description and the change is visible on a separate read.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-delete (DATABASE.md)
  intent: categories.delete removes the row so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-list (DATABASE.md)
  intent: categories.list returns rows ordered by category code ascending; two codes created in reverse order appear in sorted order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: categories-clear (DATABASE.md)
  intent: categories.clear removes categories whose code is at or above the bound, reports a positive count, and leaves none readable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-create (DATABASE.md)
  intent: transactions.create stores a signed integer-cents row under the supplied id and returns it, and a separate get reads every column back.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-get (DATABASE.md)
  intent: transactions.get returns the stored row for an existing id and None for an absent id.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-update (DATABASE.md)
  intent: transactions.update changes only the amount and the change is visible on a separate read.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-delete (DATABASE.md)
  intent: transactions.delete removes the row so a later get finds nothing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-list (DATABASE.md)
  intent: transactions.list filters by account and inclusive date range and returns rows by txn_id ascending; rows outside the range or on another account are excluded.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0
- PASS: transactions-clear (DATABASE.md)
  intent: transactions.clear removes transactions at or above the bound, reports a positive count, and leaves none readable.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/LayersTesting/runs/20261027.135355/build/LayersTesting/.venv/bin/python
  provisioning: not requested
  return code: 0

## Build summary
(no summary returned)
