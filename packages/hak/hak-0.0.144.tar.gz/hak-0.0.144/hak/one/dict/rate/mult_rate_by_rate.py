from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.one.dict.rate.is_a import f as is_rate
from hak.puvyz import f as puvyz

def f(u, v):
  if not is_rate(u): raise ValueError(f'u: {u} is not a rate')
  if not is_rate(v): raise ValueError(f'v: {v} is not a rate')

  _unit = {k: 0 for k in sorted(set(u['unit'].keys()) | set(v['unit'].keys()))}

  for k in u['unit']: _unit[k] += u['unit'][k]
  for k in v['unit']: _unit[k] += v['unit'][k]

  return make_rate(
    u[  'numerator']*v[  'numerator'],
    u['denominator']*v['denominator'],
    {k: _unit[k] for k in _unit if _unit[k] != 0}
  )

def t_a():
  u = make_rate(1, 3, {'m': 1})
  v = make_rate(3, 1, {'m': 1})
  y = make_rate(1, 1, {'m': 2})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_b():
  u = make_rate( 2,  3, {'s': 1})
  v = make_rate( 5,  7, {'s': 1})
  y = make_rate(10, 21, {'s': 2})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_c():
  u = make_rate( 13,  11, {})
  v = make_rate( 19,  17, {})
  y = make_rate(247, 187, {})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
