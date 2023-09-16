from hak.one.number.int.is_a import f as is_int
from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(x):
  if not is_int(x): return False
  if x <= 0: return False
  if x >= 10000: return False
  return True

def t_true():
  x = 2023
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false_neg():
  x = -2023
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_float():
  x = 2000.5
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_zero():
  x = 0
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_too_big():
  x = 10000
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true')
  if not t_false_neg(): return pf('!t_false_neg')
  if not t_false_float(): return pf('!t_false_float')
  if not t_false_zero(): return pf('!t_false_zero')
  if not t_false_too_big(): return pf('!t_false_too_big')
  return True
