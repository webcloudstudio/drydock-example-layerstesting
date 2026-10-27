"""Domain logic for the cash ledger.

Ownership: only the generated ``persistence`` package touches the database.
Modules here never import a database driver, and money is integer cents
everywhere; floating point is never used for money.
"""
