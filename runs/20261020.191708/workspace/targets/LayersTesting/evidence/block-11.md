# Evidence: Block 11 · Service (block-11)

- block type: block
- date: 2026-10-20
- resulting state: closed/verified
- story points (combined assembled cost): 7624
- execution id: 20261020.194114.018Z-47efe00c

## Stories built
- Execute atomic two-row account transfers. (transfers) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 755)
- implements: FEATURE-Transfers.md (SP 1091)
- context: ARCHITECTURE_compact.md (SP 154)
- context: DATABASE_compact.md (SP 163)
- stack: cli.md (SP 1755)
- stack: persistence_compact.md (SP 1217)
- stack: sqlite.md (SP 1818)

## Build directory changes
- cli/__init__.py
- data/app.db
- persistence/testing.py
- services.py
- tests/test_transfers.py

## Pre-build acceptance observation
- RED: transfers-success (FEATURE-Transfers.md)
  intent: A valid transfer creates two persisted transaction rows and succeeds.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      transactions = []
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfers-success.py", line 25, in <module>
        assert len(transactions) == 3
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: transfers-rejects-insufficient-balance (FEATURE-Transfers.md)
  intent: An insufficient-balance transfer is rejected without changing transactions.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      transactions = []
    --- drydock: end values ---
    Traceback (most recent call last):
      File "transfers-rejects-insufficient-balance.py", line 21, in <module>
        assert len(transactions) == 1
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: transfers-rejects-invalid-accounts (FEATURE-Transfers.md)
  intent: Transfers reject equal or unknown account codes before writing.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "transfers-rejects-invalid-accounts.py", line 14, in <module>
        assert cli_runner("transfer", "FROM", "FROM", "1.00", "2026-04-01")[0] == 3
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: transfers-success (FEATURE-Transfers.md)
  intent: A valid transfer creates two persisted transaction rows and succeeds.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transfers-rejects-insufficient-balance (FEATURE-Transfers.md)
  intent: An insufficient-balance transfer is rejected without changing transactions.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: transfers-rejects-invalid-accounts (FEATURE-Transfers.md)
  intent: Transfers reject equal or unknown account codes before writing.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Repair attempts
- attempt 0 (initial build): failed; 1/3 checks model=gpt-5.6-luna; execution 20261020.193838.057Z-58c5e845; reason: programmatic acceptance failed: transfers-success, transfers-rejects-insufficient-balance
- attempt 1 (repair 1): failed; 1/3 checks model=gpt-5.6-luna; execution 20261020.194006.089Z-7ed343de; reason: programmatic acceptance failed: transfers-success, transfers-rejects-insufficient-balance
- attempt 2 (repair 2): built; 3/3 checks model=gpt-5.6-luna; execution 20261020.194114.018Z-47efe00c

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- persistence/testing.py

SUMMARY:
Fixed explicit DSN sessions resetting databases before acceptance reads. Project tests pass, and all 43 terminal checks pass.

BLOCKERS:
- None
