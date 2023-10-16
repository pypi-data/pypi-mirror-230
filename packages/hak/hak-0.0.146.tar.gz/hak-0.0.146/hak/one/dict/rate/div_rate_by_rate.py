from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.puvyz import f as puvyz

def f(u, v):
  if not isinstance(u, dict): raise ValueError(f'u: {u} is not a dict')
  if not isinstance(v, dict): raise ValueError(f'v: {v} is not a dict')

  _unit = {k: 0 for k in sorted(set(u['unit'].keys()) | set(v['unit'].keys()))}

  for k in u['unit']: _unit[k] += u['unit'][k]
  for k in v['unit']: _unit[k] -= v['unit'][k]

  __unit = {k: _unit[k] for k in _unit if _unit[k] != 0}

  return make_rate(
    u[  'numerator']*v['denominator'],
    u['denominator']*v[  'numerator'],
    __unit
  )

def t_a():
  u = make_rate(1, 2, {'a': 1})
  v = make_rate(1, 3, {'b': 1})
  y = make_rate(3, 2, {'a': 1, 'b': -1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_b():
  u = make_rate( 2,  5, {'a': 1})
  v = make_rate( 7,  9, {'b': 1})
  y = make_rate(18, 35, {'a': 1, 'b': -1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_c():
  u = make_rate( 2,  5, {'USD': 1, 'RHI': -1})
  v = make_rate( 7,  9, {'USD': 1, 'AUD': -1})
  y = make_rate(18, 35, {'AUD': 1, 'RHI': -1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
