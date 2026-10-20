from __future__ import annotations
from collections import defaultdict
from persistence import Database

def balances(db: Database):
    txns = db.transactions.list(); grouped = defaultdict(list)
    for row in txns: grouped[row.account].append(row)
    return [(a.account, a.name, len(grouped[a.account]), sum(x.amount for x in grouped[a.account])) for a in db.accounts.list()]

def categories(db: Database):
    txns = db.transactions.list(); result = []
    for c in db.categories.list():
        rows = [x for x in txns if x.category == c.category]
        inflow = sum(x.amount for x in rows if x.amount > 0); outflow = -sum(x.amount for x in rows if x.amount < 0)
        result.append((c.category, c.description, len(rows), inflow, outflow, inflow-outflow))
    return result

def monthly(db: Database):
    grouped = defaultdict(list)
    for row in db.transactions.list(): grouped[row.date[:7]].append(row)
    result = []
    for month in sorted(grouped):
        rows = grouped[month]; inflow = sum(x.amount for x in rows if x.amount > 0); outflow = -sum(x.amount for x in rows if x.amount < 0)
        result.append((month, len(rows), inflow, outflow, inflow-outflow))
    return result
