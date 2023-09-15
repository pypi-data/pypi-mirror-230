from hak.pf import f as pf
from hak.pxyz import f as pxyz

# src.string.money.to_float
f = lambda x: float(x.strip().replace('$', '')) if x else 0.0

def t_0():
  x = ''
  y = 0.0
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = ' $200.00 '
  y = 200.0
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = '$ 300.00 '
  y = 300.0
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  return True
