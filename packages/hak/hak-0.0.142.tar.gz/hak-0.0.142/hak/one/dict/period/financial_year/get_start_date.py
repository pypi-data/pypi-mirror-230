from datetime import date

from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_α_date
f = lambda x: date(x['financial_year']['start_year'], 7, 1)

def t_a():
  x = {'financial_year': mkfy({'start_year': 2022})}
  y = date(2022, 7, 1)
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  x = {'financial_year': mkfy({'final_year': 2022})}
  y = date(2021, 7, 1)
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  return True
