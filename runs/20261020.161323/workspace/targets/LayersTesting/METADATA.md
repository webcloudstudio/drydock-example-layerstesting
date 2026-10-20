# AUTHORITATIVE PROJECT METADATA — FIELDS SHOULD BE CURRENT

name: LayersTesting
display_name: drydock Layers Testing Uat Case
short_description: Drydock uat - LayersTesting exercises the language and persistence layers. The source is an original brief for a command-line cash ledger with three tables (accounts, categories, transactions) reached only through the shipped persistence library. The supplied grader, sources/run.sh, initializes a fresh database, loads 131 known rows, and runs 43 checks of exit code and output: row counts, three reports with known totals, create/read/update/delete on accounts and transactions, atomic rejected loads and transfers, the non-negative balance rule, and a final drop and recreate. This build is in Python over SQLite. Run with drydock uat LayersTesting. Source Repo: none, the brief is original to this kit.
stack: Python
version: 0.09
build_state: building
build_sub_state: running
last_analyzed: 2026-10-20
last_planned: 2026-10-20
last_built: 
build_dir: 
brand: 
git_repo: 
release_tag: 
updated: 2026-10-20T16:18:35+00:00
