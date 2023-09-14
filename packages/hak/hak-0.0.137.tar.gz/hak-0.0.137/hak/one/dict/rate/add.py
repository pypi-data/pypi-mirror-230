from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.puvyz import f as puvyz

def f(u, v):
  if not isinstance(u, dict): raise ValueError(f'u: {u} is not a dict')
  if not isinstance(v, dict): raise ValueError(f'v: {v} is not a dict')

  if u['unit'] != v['unit']:
    raise ValueError(f"u['unit']: {u['unit']} != v['unit']: {v['unit']}")

  n = 'numerator'
  d = 'denominator'

  return make_rate(u[n] * v[d] + v[n] * u[d], u[d] * v[d], u['unit'])

def t_a():
  u = make_rate(1, 2, {'a': 1})
  v = make_rate(1, 3, {'a': 1})
  y = make_rate(5, 6, {'a': 1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_b():
  u = make_rate( 2,  5, {'b': 1})
  v = make_rate( 7,  9, {'b': 1})
  y = make_rate(53, 45, {'b': 1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_different_units():
  u = make_rate( 2,  5, {'a': 1})
  v = make_rate( 7,  9, {'b': 1})
  y = "u['unit']: {'a': 1} != v['unit']: {'b': 1}"
  try: z = f(u, v)
  except ValueError as ve: z = str(ve)
  return puvyz(u, v, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_different_units(): return pf('!t_different_units')
  return True
