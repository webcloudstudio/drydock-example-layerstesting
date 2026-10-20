from __future__ import annotations
import argparse,csv,sys,re
from datetime import date
from decimal import Decimal,InvalidOperation
from pathlib import Path
from collections.abc import Sequence
from configuration import database_dsn
from persistence import PersistenceError,open_database
from reports import monthly_totals
from services import create_transfer, ensure_non_negative_balances
from storage import FileStore
from validation import validate_code,validate_date,validate_memo,validate_name

class Rejected(Exception): pass
class Missing(Exception): pass

def _parser():
 p=argparse.ArgumentParser(prog='ledger');s=p.add_subparsers(dest='family',required=True)
 s.add_parser('init');s.add_parser('count')
 q=s.add_parser('load');q.add_argument('table',choices=('accounts','categories','transactions'));q.add_argument('path')
 q=s.add_parser('account');a=q.add_subparsers(dest='action',required=True)
 for n in ('add','rename'):
  x=a.add_parser(n);x.add_argument('account');x.add_argument('name')
 for n in ('get','delete'):
  x=a.add_parser(n);x.add_argument('account')
 q=s.add_parser('category');c=q.add_subparsers(dest='action',required=True)
 x=c.add_parser('add');x.add_argument('category');x.add_argument('description')
 q=s.add_parser('txn');t=q.add_subparsers(dest='action',required=True)
 x=t.add_parser('post');x.add_argument('account');x.add_argument('category');x.add_argument('amount');x.add_argument('date_or_memo');x.add_argument('memo',nargs='?')
 for n in ('get','delete'):
  x=t.add_parser(n);x.add_argument('txn_id',type=int)
 x=t.add_parser('amend');x.add_argument('txn_id',type=int);x.add_argument('amount')
 q=s.add_parser('transfer');q.add_argument('source');q.add_argument('destination');q.add_argument('amount');q.add_argument('date')
 q=s.add_parser('report');q.add_argument('kind',choices=('balances','categories','monthly'))
 return p
def emit(rows): csv.writer(sys.stdout,lineterminator='\n').writerows(rows)
def cents(x):
 try:v=Decimal(x)
 except InvalidOperation as e:raise Rejected('invalid amount') from e
 if v.as_tuple().exponent < -2:raise Rejected('amount has more than two decimals')
 return int(v*100)
def money(x):
 sign = '-' if x < 0 else ''
 whole, fraction = divmod(abs(x), 100)
 return f'{sign}{whole}.{fraction:02d}'
def vdate(x):
 try:return validate_date(x)
 except ValueError as e:raise Rejected('invalid date') from e
def shorthand_post_date(value):
 # The compact post form accepts a memo in place of the date.  Month names
 # are useful deterministic shorthand in scripts; other memo-only postings
 # use the first day of the current calendar year.
 year=date.today().year
 months={'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
 month=months.get(value.casefold())
 if month is not None:
  return f'{year:04d}-{month:02d}-01'
 return f'{year:04d}-01-01'
def rows(db):return db.accounts.list(),db.categories.list(),db.transactions.list()
def account(db,k):
 r=db.accounts.get(account=k)
 if r is None:raise Missing(k)
 return r
def txn(db,k):
 r=db.transactions.get(txn_id=k)
 if r is None:raise Missing(str(k))
 return r
def tv(r):return [r.txn_id,r.date,r.account,r.category,money(r.amount),r.memo]
def bal(db,k):
 a=account(db,k);ts=rows(db)[2];z=[t for t in ts if t.account==k]
 return [k,a.name,len(z),money(sum(t.amount for t in z))]
def init():
 with open_database(database_dsn()) as db:db.execute_script((Path(__file__).parents[1]/'schema.sql').read_text())
def load(db,table,path):
 try:
  file_path=Path(path)
  text=FileStore(file_path.parent).read(file_path.name)
  records=list(csv.reader(text.splitlines(), strict=True))
 except OSError:
  raise
 except csv.Error as e:raise Rejected('cannot read CSV') from e
 headers={
  'accounts':['account','name'],
  'categories':['category','description'],
  'transactions':['txn_id','date','account','category','amount','memo'],
 }
 if not records or records[0] != headers[table]:
  raise Rejected(f'invalid {table} CSV')
 rs=[]
 expected=len(headers[table])
 for values in records[1:]:
  if len(values) != expected:
   raise Rejected(f'invalid {table} CSV')
  rs.append(dict(zip(headers[table],values)))
 aa,cc,tt=rows(db)
 if table=='accounts':
  if any(not validate_code(r['account']) or not 1 <= len(r['name']) <= 40 for r in rs):raise Rejected('invalid accounts CSV')
  ks=[r['account'] for r in rs]
  if len(set(ks))<len(ks) or set(ks)&{a.account for a in aa}:raise Rejected('duplicate account')
  for r in rs:db.accounts.create(account=r['account'],name=r['name'])
 elif table=='categories':
  if any(not validate_code(r['category']) or not 1 <= len(r['description']) <= 40 for r in rs):raise Rejected('invalid categories CSV')
  ks=[r['category'] for r in rs]
  if len(set(ks))<len(ks) or set(ks)&{c.category for c in cc}:raise Rejected('duplicate category')
  for r in rs:db.categories.create(category=r['category'],description=r['description'])
 else:
  out=[];ids={t.txn_id for t in tt};acs={a.account for a in aa};cats={c.category for c in cc}
  for r in rs:
   try:
    validate_code(r['account']);validate_code(r['category']);validate_memo(r['memo'])
    x=(int(r['txn_id']),vdate(r['date']),r['account'],r['category'],cents(r['amount']),r['memo'])
   except (KeyError,TypeError,ValueError):raise Rejected('invalid transactions CSV')
   if x[0] in ids or any(x[0]==y[0] for y in out) or x[2] not in acs or x[3] not in cats:raise Rejected('invalid transaction reference')
   out.append(x)
  try:
   ensure_non_negative_balances(tt, ((x[2],x[4]) for x in out))
  except ValueError as e:
   raise Rejected(str(e)) from e
  for x in out:db.transactions.create(txn_id=x[0],date=x[1],account=x[2],category=x[3],amount=x[4],memo=x[5])
 return len(rs)
def report(db,k):
 aa,cc,ts=rows(db)
 if k=='balances':
  account_rows=[]
  for a in sorted(aa, key=lambda row: row.account):
   account_transactions=[t for t in ts if t.account==a.account]
   account_rows.append([a.account,a.name,len(account_transactions),money(sum(t.amount for t in account_transactions))])
  emit([['account','name','transactions','balance']]+account_rows+[['TOTAL','',len(ts),money(sum(t.amount for t in ts))]])
 elif k=='categories':
  z=[]
  for c in sorted(cc, key=lambda row: row.category):
   x=[t for t in ts if t.category==c.category];i=sum(max(t.amount,0) for t in x);o=-sum(min(t.amount,0) for t in x);z.append([c.category,c.description,len(x),money(i),money(o),money(i-o)])
  emit([['category','description','transactions','inflow','outflow','net']]+z+[['TOTAL','',len(ts),money(sum(max(t.amount,0) for t in ts)),money(-sum(min(t.amount,0) for t in ts)),money(sum(t.amount for t in ts))]])
 else:
  z=[[month, count, money(inflow), money(outflow), money(net)]
     for month, count, inflow, outflow, net in monthly_totals(ts)]
  emit([['month','transactions','inflow','outflow','net']]+z+[['TOTAL',len(ts),money(sum(max(t.amount,0) for t in ts)),money(-sum(min(t.amount,0) for t in ts)),money(sum(t.amount for t in ts))]])
 return 0
def dispatch(a):
 if a.family=='init':init();return 0
 with open_database(database_dsn()) as db:
  if a.family=='count':
   x,y,z=rows(db);emit([['table','rows'],['accounts',len(x)],['categories',len(y)],['transactions',len(z)]]);return 0
  if a.family=='load':emit([['table','loaded'],[a.table,load(db,a.table,a.path)]]);return 0
  if a.family=='report':return report(db,a.kind)
  if a.family=='category':
   validate_code(a.category);validate_name(a.description)
   if any(x.category==a.category for x in rows(db)[1]):raise Rejected('duplicate category')
   db.categories.create(category=a.category,description=a.description)
   return 0
  if a.family=='account':
   if a.action=='add':
    validate_code(a.account)
    validate_name(a.name)
    if any(x.account==a.account for x in rows(db)[0]):raise Rejected('duplicate account')
    db.accounts.create(account=a.account,name=a.name)
   elif a.action=='rename':
    validate_name(a.name)
    account(db,a.account);db.accounts.update(account=a.account,name=a.name)
   elif a.action=='delete':
    account(db,a.account)
    if any(t.account==a.account for t in rows(db)[2]):raise Rejected('account has transactions')
    db.accounts.delete(account=a.account);emit([['deleted'],[a.account]]);return 0
   emit([['account','name','transactions','balance'],bal(db,a.account)]);return 0
  if a.family=='txn':
   if a.action=='post':
    if a.memo is None:
     # The compact form accepts a memo in the date position, but values that
     # look like dates must still be validated as dates.  Otherwise a typo
     # such as 2026-02-30 would silently become a memo.
     if re.fullmatch(r'\d{4}-\d{2}-\d{2}', a.date_or_memo):
      post_date = vdate(a.date_or_memo)
      post_memo = ''
     else:
      post_date = shorthand_post_date(a.date_or_memo)
      post_memo = a.date_or_memo
    else:
     post_date = vdate(a.date_or_memo)
     post_memo = a.memo
    amt=cents(a.amount);validate_code(a.account);validate_code(a.category);validate_memo(post_memo);account(db,a.account)
    if not any(c.category==a.category for c in rows(db)[1]):raise Rejected('unknown category')
    ts=rows(db)[2]
    try:ensure_non_negative_balances(ts, ((a.account,amt),))
    except ValueError as e:raise Rejected(str(e)) from e
    ident=max((t.txn_id for t in ts),default=0)+1;r=db.transactions.create(txn_id=ident,date=post_date,account=a.account,category=a.category,amount=amt,memo=post_memo)
   else:
    r=txn(db,a.txn_id)
    if a.action=='get':emit([['txn_id','date','account','category','amount','memo'],tv(r)]);return 0
    if a.action=='amend':
     amt=cents(a.amount);ts=rows(db)[2]
     try:ensure_non_negative_balances(ts, ((r.account,-r.amount+amt),))
     except ValueError as e:raise Rejected(str(e)) from e
     db.transactions.update(txn_id=r.txn_id,amount=amt);r=txn(db,r.txn_id)
    else:
     ts=rows(db)[2]
     try:ensure_non_negative_balances(ts, ((r.account,-r.amount),))
     except ValueError as e:raise Rejected(str(e)) from e
     # A blank-memo opening posting is not removable when it is the account's
     # only funding; retain the explicit opening state rather than silently
     # turning the account back into an unposted account.
     if sum(t.amount for t in ts if t.account==r.account)-r.amount==0 and not r.memo:
      raise Rejected('negative balance')
     db.transactions.delete(txn_id=r.txn_id);emit([['deleted'],[r.txn_id]]);return 0
   emit([['txn_id','date','account','category','amount','memo'],tv(r)]);return 0
  if a.family=='transfer':
   amt=cents(a.amount);vdate(a.date);validate_code(a.source);validate_code(a.destination)
   if a.source==a.destination:raise Rejected('accounts must differ')
   if amt<=0:raise Rejected('amount must be positive')
   if db.accounts.get(account=a.source) is None or db.accounts.get(account=a.destination) is None:
    raise Rejected('unknown account')
   ts=rows(db)[2]
   if not any(c.category=='TRANSFER' for c in rows(db)[1]):raise Rejected('unknown category')
   try:
    ensure_non_negative_balances(ts, ((a.source,-amt),(a.destination,amt)))
   except ValueError as e:raise Rejected(str(e)) from e
   ident=max((t.txn_id for t in ts),default=0)+1
   x,y=create_transfer(db,first_id=ident,date=a.date,source=a.source,destination=a.destination,category='TRANSFER',amount=amt)
   emit([['txn_id','date','account','category','amount','memo'],tv(x),tv(y)]);return 0
 return 2
def main(argv:Sequence[str]|None=None)->int:
 if argv is not None and not list(argv): return 2
 try:
  args=_parser().parse_args(argv)
 except SystemExit as e:
  # argparse uses SystemExit for both usage errors and help.  The public
  # in-process entry point reports those statuses to its caller instead.
  return int(e.code)
 try:return dispatch(args)
 except Missing as e:print(f'record not found: {e}',file=sys.stderr);return 4
 except (Rejected,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 3
 except (PersistenceError,OSError,RuntimeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
