from datetime import date
from datetime import datetime as dt

from hak.one.dict.period.financial_year.get_end_date import f as get_ω_d
from hak.one.dict.period.financial_year.get_start_date import f as get_α_d
from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# contains_date
f = lambda x: (
  get_α_d(x) <= (
    x['date'].date() if isinstance(x['date'], dt) else
    x['date']
  ) <= get_ω_d(x)
)

def t_true():
  x = {'financial_year': mkfy({'start_year': 2022}), 'date': date(2022, 7, 5)}
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false():
  x = {'financial_year': mkfy({'start_year': 2022}), 'date': date(2022, 6, 5)}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true()')
  if not t_false(): return pf('!t_false()')
  return True
