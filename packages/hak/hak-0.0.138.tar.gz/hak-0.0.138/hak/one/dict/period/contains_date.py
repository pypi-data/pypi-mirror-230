from datetime import date

from hak.one.dict.period.financial_year.contains_date import f as d_in_fy
from hak.one.dict.period.financial_year.make import f as mkfy
from hak.one.dict.period.month.contains_date import f as d_in_m
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# contains_d
f = lambda x: (d_in_m if 'month' in x else d_in_fy)(x)

def t_fy_true():
  x = {'financial_year': mkfy({'start_year': 2022}), 'date': date(2022, 7, 5)}
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_fy_false():
  x = {'financial_year': mkfy({'start_year': 2022}), 'date': date(2022, 6, 5)}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_month():
  x = {'month': {'year': 2022, 'number': 1}, 'date': date(2022, 1, 10)}
  y = True
  z = f(x)
  return y == z or pf(f'expected {x["date"]} to be in {x["month"]}')

def t():
  if not t_fy_true(): return pf('!t_fy_true()')
  if not t_fy_false(): return pf('!t_fy_false()')
  if not t_month(): return pf('!t_month()')
  return True
