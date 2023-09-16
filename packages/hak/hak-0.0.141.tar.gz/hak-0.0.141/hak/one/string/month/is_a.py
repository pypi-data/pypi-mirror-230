from hak.data.months import months
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# src.string.month.is_a
# is_month
def f(x):
  x = x.lower()[:3]
  months_list = [m[:3].lower() for m in months]
  if x in set(months_list): return True
  return 1 <= int(x) <= 12 if x.isdecimal() else False

def t_0():
  x = 'Apr'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = 'April'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = '04'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = '4'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = '0'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_5():
  x = '13'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  if not t_5(): return pf('t_5 failed')
  return True
