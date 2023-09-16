from datetime import date

from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pf import f as pf
from hak.pxyz import f as pxyz

f = lambda x: mkfy({'final_year': x.year + (x.month > 6)})

def t_july():
  x = date(2022, 7, 1)
  y = {'start_year': 2022, 'final_year': 2023}
  z = f(x)
  return pxyz(x, y, z)

def t_june():
  x = date(2022, 6, 30)
  y = {'start_year': 2021, 'final_year': 2022}
  z = f(x)
  return pxyz(x, y, z)

t_barrage = lambda: all([
  f(date(1999,  1,  1)) == {'start_year': 1998, 'final_year': 1999},
  f(date(1999,  6, 30)) == {'start_year': 1998, 'final_year': 1999},
  f(date(1999,  7,  1)) == {'start_year': 1999, 'final_year': 2000},
  f(date(1999, 12, 31)) == {'start_year': 1999, 'final_year': 2000},
  f(date(2000,  1,  1)) == {'start_year': 1999, 'final_year': 2000},
  f(date(2000,  6, 30)) == {'start_year': 1999, 'final_year': 2000},
  f(date(2000,  7,  1)) == {'start_year': 2000, 'final_year': 2001},
  f(date(2000, 12, 31)) == {'start_year': 2000, 'final_year': 2001},
  True
])

def t():
  if not t_july(): return pf('!t_july')
  if not t_june(): return pf('!t_june')
  if not t_barrage(): return pf('!t_barrage')
  return True
