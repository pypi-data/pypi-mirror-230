from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.pxyz import f as pxyz

def f(x):
  if not isinstance(x, dict): return False
  if not 'numerator' in x: return False
  if not 'denominator' in x: return False
  if not 'unit' in x: return False
  return True

def t_true():
  x = make_rate(1, 2, {})
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_true_units():
  x = make_rate(1, 2, {'m': 2, 's': -1})
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false():
  x = 'abc'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true()')
  if not t_true_units(): return pf('!t_true_units()')
  if not t_false(): return pf('!t_false()')
  return True
