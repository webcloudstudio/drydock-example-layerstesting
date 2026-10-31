# LAYERSTESTING

- Short description: Drydock uat - LayersTesting exercises the language and persistence layers. The source is an original brief for a command-line cash ledger with three tables (accounts, categories, transactions) reached only through the shipped persistence library. The supplied grader, sources/run.sh, initializes a fresh database, loads 131 known rows, and runs 43 checks of exit code and output: row counts, three reports with known totals, create/read/update/delete on accounts and transactions, atomic rejected loads and transfers, the non-negative balance rule, and a final ledger reset. This build is in Python over SQLite. Run with drydock uat LayersTesting. Source Repo: none, the brief is original to this kit.
- Status: PROJECT COMPLETE

4 of 4 receipt claims proven. Open `index.html` for the linked proof kit; verify it with `sha256sum -c SHA256SUMS`.

## Receipt

| Claim | Verdict | Recorded outcome | Proof |
|---|---|---|---|
| Lifecycle completed | PASS | 21 lifecycle commands executed; the run ended at 21-score-release. | [result.json](result.json) |
| External conformance suite passed | PASS | sh sources/run.sh exited 0. | [evidence/commands/18-test.stdout.log](evidence/commands/18-test.stdout.log) |
| Release score passed | PASS | drydock score release exited 0. | [evidence/commands/21-score-release.stdout.log](evidence/commands/21-score-release.stdout.log) |
| Integrity verification passed | PASS | 851 files digested; verify with sha256sum -c SHA256SUMS. | [SHA256SUMS](SHA256SUMS) |

## Run facts

- Drydock: `0.8.0` (commit `c62f2e158c62b51800e7a80ad02746d14a40f381`)
- Provider and model: `claude` / `claude-haiku-5-5, claude-sonnet-5-5`
- Platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35` on Python `3.12.13`
- Run: `20261027.135355`
- Elapsed: 4648.1s
- LLM calls: 26
- Tokens: cached 7,896,770; uncached 310; output 326,964
- LLM elapsed: 3050.4s
- Build passes: 1; repairs: 6 attempts allowed
- Conformance: passed
- Advisory scores: acceptance=exit 0, build-report=exit 0, release=exit 0

## RUN SUMMARY

- Input specification: [`sources/INSTRUCTIONS.md`](sources/INSTRUCTIONS.md)
- Delivered Code: [`build/LayersTesting/`](build/LayersTesting)
- Test Results: [`evidence/commands/18-test.stdout.log`](evidence/commands/18-test.stdout.log)

## Commands

| # | Command | Exit | Elapsed | Output |
|---|---|---|---|---|
| 01-init | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock init LayersTesting` | 0 | 3.7s | [stdout](evidence/commands/01-init.stdout.log) · [stderr](evidence/commands/01-init.stderr.log) |
| 02-import-sources | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock import LayersTesting sources --format markdown` | 0 | 6.6s | [stdout](evidence/commands/02-import-sources.stdout.log) · [stderr](evidence/commands/02-import-sources.stderr.log) |
| 03-analyze | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock analyze LayersTesting` | 0 | 34.8s | [stdout](evidence/commands/03-analyze.stdout.log) · [stderr](evidence/commands/03-analyze.stderr.log) · [llm](evidence/commands/03-analyze.llm.log) |
| 04-plan | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan LayersTesting --override --plan-override-model sonnet` | 0 | 910.6s | [stdout](evidence/commands/04-plan.stdout.log) · [stderr](evidence/commands/04-plan.stderr.log) · [llm](evidence/commands/04-plan.llm.log) |
| 05-plan-verify | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan verify LayersTesting --plan-override-model sonnet` | 1 | 106.3s | [stdout](evidence/commands/05-plan-verify.stdout.log) · [stderr](evidence/commands/05-plan-verify.stderr.log) |
| 06-plan-repair | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan repair LayersTesting --plan-override-model sonnet` | 0 | 237.9s | [stdout](evidence/commands/06-plan-repair.stdout.log) · [stderr](evidence/commands/06-plan-repair.stderr.log) · [llm](evidence/commands/06-plan-repair.llm.log) |
| 07-plan-verify-after-repair | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan verify LayersTesting --plan-override-model sonnet` | 0 | 105.6s | [stdout](evidence/commands/07-plan-verify-after-repair.stdout.log) · [stderr](evidence/commands/07-plan-verify-after-repair.stderr.log) |
| 08-after-plan-build-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock build status LayersTesting` | 0 | 2.3s | [stdout](evidence/commands/08-after-plan-build-status.stdout.log) · [stderr](evidence/commands/08-after-plan-build-status.stderr.log) |
| 09-after-plan-target-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status LayersTesting` | 0 | 3.2s | [stdout](evidence/commands/09-after-plan-target-status.stdout.log) · [stderr](evidence/commands/09-after-plan-target-status.stderr.log) |
| 10-after-plan-workspace-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status` | 0 | 1.4s | [stdout](evidence/commands/10-after-plan-workspace-status.stdout.log) · [stderr](evidence/commands/10-after-plan-workspace-status.stderr.log) |
| 11-initial-ready | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status LayersTesting --ready` | 0 | 3.9s | [stdout](evidence/commands/11-initial-ready.stdout.log) · [stderr](evidence/commands/11-initial-ready.stderr.log) |
| 12-initial-build-1 | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock build LayersTesting --override --repair-attempts 6` | 0 | 3023.1s | [stdout](evidence/commands/12-initial-build-1.stdout.log) · [stderr](evidence/commands/12-initial-build-1.stderr.log) · [llm](evidence/commands/12-initial-build-1.llm.log) |
| 13-initial-ready | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status LayersTesting --ready` | 1 | 1.9s | [stdout](evidence/commands/13-initial-ready.stdout.log) · [stderr](evidence/commands/13-initial-ready.stderr.log) |
| 14-initial-complete | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status LayersTesting --check` | 1 | 1.3s | [stdout](evidence/commands/14-initial-complete.stdout.log) · [stderr](evidence/commands/14-initial-complete.stderr.log) |
| 15-after-initial-build-build-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock build status LayersTesting` | 0 | 1.2s | [stdout](evidence/commands/15-after-initial-build-build-status.stdout.log) · [stderr](evidence/commands/15-after-initial-build-build-status.stderr.log) |
| 16-after-initial-build-target-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status LayersTesting` | 0 | 2.6s | [stdout](evidence/commands/16-after-initial-build-target-status.stdout.log) · [stderr](evidence/commands/16-after-initial-build-target-status.stderr.log) |
| 17-after-initial-build-workspace-status | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock status` | 0 | 1.3s | [stdout](evidence/commands/17-after-initial-build-workspace-status.stdout.log) · [stderr](evidence/commands/17-after-initial-build-workspace-status.stderr.log) |
| 18-test | `sh sources/run.sh` | 0 | 16.2s | [stdout](evidence/commands/18-test.stdout.log) · [stderr](evidence/commands/18-test.stderr.log) |
| 19-score-acceptance | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock score ac LayersTesting` | 0 | 99.8s | [stdout](evidence/commands/19-score-acceptance.stdout.log) · [stderr](evidence/commands/19-score-acceptance.stderr.log) |
| 20-score-build-report | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock score build LayersTesting` | 0 | 0.6s | [stdout](evidence/commands/20-score-build-report.stdout.log) · [stderr](evidence/commands/20-score-build-report.stderr.log) |
| 21-score-release | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock score release LayersTesting` | 0 | 75.7s | [stdout](evidence/commands/21-score-release.stdout.log) · [stderr](evidence/commands/21-score-release.stderr.log) · [llm](evidence/commands/21-score-release.llm.log) |

## Evidence

- [`evidence/commands/`](evidence/commands) — stdout and stderr of every command
- [`evidence/prompts/`](evidence/prompts) — the assembled prompt for every LLM call
- [`evidence/provider_raw/`](evidence/provider_raw) — unmodified provider transcripts
- [`evidence/llm_logs/`](evidence/llm_logs) — call banners and token accounting
- [`result.json`](result.json) — the machine-readable record of this run
