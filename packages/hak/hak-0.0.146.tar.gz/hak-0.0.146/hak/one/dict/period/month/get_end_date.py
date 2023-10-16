from datetime import date
from datetime import timedelta

from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_ω_date_of_month
f = lambda x: (
  date(
    year=x['month']['year'],
    month=x['month']['number']+1,
    day=1
  ) - timedelta(days=1)
  if x['month']['number'] < 12 else
  date(year=x['month']['year']+1, month=1, day=1) - timedelta(days=1)
)

def t_0():
  x = {'month': {'year': 2016, 'number':  5}}
  y = date(2016,  5, 31)
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = {'month': {'year': 2017, 'number':  6}}
  y = date(2017,  6, 30)
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = {'month': {'year': 2020, 'number':  2}}
  y = date(2020,  2, 29)
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = {'month': {'year': 2021, 'number':  2}}
  y = date(2021,  2, 28)
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = {'month': {'year': 2021, 'number': 12}}
  y = date(2021, 12, 31)
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('!t_0')
  if not t_1(): return pf('!t_1')
  if not t_2(): return pf('!t_2')
  if not t_3(): return pf('!t_3')
  if not t_4(): return pf('!t_4')
  return True
