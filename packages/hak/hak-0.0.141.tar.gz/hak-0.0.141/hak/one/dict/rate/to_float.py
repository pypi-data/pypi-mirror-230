from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.pxyz import f as pxyz

def f(x):
  if x['denominator'] == 0: raise ZeroDivisionError('denominator must not be 0')
  return x['numerator']/x['denominator']

def t_int_as_float():
  x = make_rate(2, 1, {})
  y = type(2.0)
  z = type(f(x))
  return pxyz(x, y, z)

def t_float():
  x = make_rate(1, 2, {})
  y = type(0.5)
  z = type(f(x))
  return pxyz(x, y, z)

def t():
  if not t_int_as_float(): return pf('!t_int_as_float')
  if not t_float(): return pf('!t_float')
  return True
