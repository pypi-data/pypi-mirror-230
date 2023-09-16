from hak.pf import f as pf
from hak.pxyz import f as pxyz

# src.string.day.is_a
# is_year
f = lambda x: 1 <= int(x) <= 31 if x.isdecimal() else False

def t_0():
  x = 'Apr'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = 'April'
  y = False
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
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_6():
  x = '31'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_7():
  x = '32'
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
  if not t_6(): return pf('t_6 failed')
  if not t_7(): return pf('t_7 failed')
  return True
