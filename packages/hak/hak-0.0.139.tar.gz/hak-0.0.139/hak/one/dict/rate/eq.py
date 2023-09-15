from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.puvyz import f as puvyz

# __eq__
f = lambda u, v: make_rate(**u) == make_rate(**v)

def t_true_a():
  u = make_rate(  1,   2, {'1': 0})
  v = make_rate(1.0, 2.0, {'1': 0})
  y = True
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_true_b():
  u = make_rate( 0.25, 0.5, {'1': 0})
  v = make_rate(10, 20, {'1': 0})
  y = True
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_false():
  u = make_rate(1, 2, {'1': 0})
  v = make_rate(2, 3, {'1': 0})
  y = False
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_false_different_units():
  u = make_rate(1, 2, {'a': 1})
  v = make_rate(2, 3, {'b': 1})
  y = False
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_true_a(): return pf('!t_true()')
  if not t_true_b(): return pf('!t_true()')
  if not t_false(): return pf('!t_false()')
  if not t_false_different_units(): return pf('!t_false_different_units')
  return True
