from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.pxyz import f as pxyz

def f(x):
  if not isinstance(x, dict): raise ValueError(f'x: {x} is not a dict')
  return make_rate(abs(x['numerator']), abs(x['denominator']), x['unit'])

def t_a():
  x = make_rate(-1, 3, {'a': 1})
  y = make_rate( 1, 3, {'a': 1})
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  x = make_rate(45, -7, {'b': 1})
  y = make_rate(45,  7, {'b': 1})
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  return True
