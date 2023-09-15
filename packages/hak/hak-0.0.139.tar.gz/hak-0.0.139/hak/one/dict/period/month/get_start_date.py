from datetime import date

from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_first_date_of_month
f = lambda x: date(year=x['month']['year'], month=x['month']['number'], day=1)

def t_0():
  x = {'month': {'year': 2016, 'number':  5}}
  y = date(2016,  5, 1)
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = {'month': {'year': 2017, 'number':  6}}
  y = date(2017,  6, 1)
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = {'month': {'year': 2020, 'number':  2}}
  y = date(2020,  2, 1)
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = {'month': {'year': 2021, 'number':  2}}
  y = date(2021,  2, 1)
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = {'month': {'year': 2021, 'number': 12}}
  y = date(2021, 12, 1)
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('!t_0')
  if not t_1(): return pf('!t_1')
  if not t_2(): return pf('!t_2')
  if not t_3(): return pf('!t_3')
  if not t_4(): return pf('!t_4')
  return True
