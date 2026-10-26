# LAYERSTESTING

- Short description: Drydock uat - LayersTesting exercises the language and persistence layers. The source is an original brief for a command-line cash ledger with three tables (accounts, categories, transactions) reached only through the shipped persistence library. The supplied grader, sources/run.sh, initializes a fresh database, loads 131 known rows, and runs 43 checks of exit code and output: row counts, three reports with known totals, create/read/update/delete on accounts and transactions, atomic rejected loads and transfers, the non-negative balance rule, and a final ledger reset. This build is in Python over SQLite. Run with drydock uat LayersTesting. Source Repo: none, the brief is original to this kit.
- Status: BLOCKED: UAT STAGE

1 of 4 receipt claims proven. Open `index.html` for the linked proof kit; verify it with `sha256sum -c SHA256SUMS`.

## Receipt

| Claim | Verdict | Recorded outcome | Proof |
|---|---|---|---|
| Lifecycle completed | FAIL | 8 lifecycle commands executed; the run ended at 08-after-plan-build-status. | [result.json](result.json) |
| External conformance suite passed | UNPROVEN | The configured external conformance suite was not executed. | — |
| Release score passed | UNPROVEN | No release score was recorded for this run. | — |
| Integrity verification passed | PASS | 279 files digested; verify with sha256sum -c SHA256SUMS. | [SHA256SUMS](SHA256SUMS) |

## Run facts

- Drydock: `0.8.0` (commit `0338ebe4b83fc8b1295d7a1be92f83c44deff55a`)
- Provider and model: `claude` / `claude-haiku-5-5, claude-sonnet-5-5`
- Platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35` on Python `3.12.13`
- Run: `20261026.213305`
- Elapsed: 1627.0s
- LLM calls: 16
- Tokens: cached 23,250; uncached 32; output 170,245
- LLM elapsed: 996.2s
- Build passes: 0; repairs: not recorded
- Conformance: not executed
- Advisory scores: none recorded

## RUN SUMMARY

- Input specification: [`sources/INSTRUCTIONS.md`](sources/INSTRUCTIONS.md)
- Delivered Code: [`build/LayersTesting/`](build/LayersTesting)
- Test Results: not recorded for this run.

## Shortfall

- Failure: LayersTesting: stopped at plan-repair: acceptance criteria still cannot run after one repair pass

## Commands

| # | Command | Exit | Elapsed | Output |
|---|---|---|---|---|
| 01-init | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock init LayersTesting` | 0 | 3.8s | [stdout](evidence/commands/01-init.stdout.log) · [stderr](evidence/commands/01-init.stderr.log) |
| 02-import-sources | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock import LayersTesting sources --format markdown` | 0 | 7.1s | [stdout](evidence/commands/02-import-sources.stdout.log) · [stderr](evidence/commands/02-import-sources.stderr.log) |
| 03-analyze | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock analyze LayersTesting` | 0 | 184.0s | [stdout](evidence/commands/03-analyze.stdout.log) · [stderr](evidence/commands/03-analyze.stderr.log) · [llm](evidence/commands/03-analyze.llm.log) |
| 04-plan | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan LayersTesting --override --plan-override-model sonnet` | 0 | 978.4s | [stdout](evidence/commands/04-plan.stdout.log) · [stderr](evidence/commands/04-plan.stderr.log) · [llm](evidence/commands/04-plan.llm.log) |
| 05-plan-verify | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan verify LayersTesting --plan-override-model sonnet` | 1 | 104.6s | [stdout](evidence/commands/05-plan-verify.stdout.log) · [stderr](evidence/commands/05-plan-verify.stderr.log) |
| 06-plan-repair | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan repair LayersTesting --plan-override-model sonnet` | 1 | 225.3s | [stdout](evidence/commands/06-plan-repair.stdout.log) · [stderr](evidence/commands/06-plan-repair.stderr.log) |
| 07-plan-verify-after-repair | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan verify LayersTesting --plan-override-model sonnet` | 1 | 115.9s | [stdout](evidence/commands/07-plan-verify-after-repair.stdout.log) · [stderr](evidence/commands/07-plan-verify-after-repair.stderr.log) |
| 08-after-plan-build-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock build status LayersTesting` | 1 | 0.8s | [stdout](evidence/commands/08-after-plan-build-status.stdout.log) · [stderr](evidence/commands/08-after-plan-build-status.stderr.log) |

## Evidence

- [`evidence/commands/`](evidence/commands) — stdout and stderr of every command
- [`evidence/prompts/`](evidence/prompts) — the assembled prompt for every LLM call
- [`evidence/provider_raw/`](evidence/provider_raw) — unmodified provider transcripts
- [`evidence/llm_logs/`](evidence/llm_logs) — call banners and token accounting
- [`result.json`](result.json) — the machine-readable record of this run
