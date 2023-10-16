from datetime import date
from datetime import datetime as dt
from hak.pf import f as pf
from hak.pxyz import f as pxyz
from time import timezone

f = lambda x: dt(x.year, x.month, x.day).timestamp() - timezone

def t_0():
  x = date(1970,1,1)
  y = 0
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = date(1970,1,2)
  y = 86400
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = date(2022,3,4)
  y = 1646352000
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  return True
