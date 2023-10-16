from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.one.dict.rate.div_rate_by_rate import f as div_rate_by_rate
from hak.puvyz import f as puvyz

def f(u, v):
  if not any([isinstance(u, int), isinstance(u, float)]):
    raise ValueError(f'u: {u} is not a number')

  if not isinstance(v, dict):
    raise ValueError(f'v: {v} is not a dict')

  return div_rate_by_rate(make_rate(u, 1, {'1': 0}), v)

def t_a():
  u = 1
  v = make_rate(1, 3, {'a': 1})
  y = {'numerator': 3, 'denominator': 1, 'unit': {'a': -1}}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_b():
  u = 5
  v = make_rate( 7, 9, {'b': 1})
  y = make_rate(45, 7, {'b': -1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  return True
