from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate
from hak.one.dict.rate.is_a import f as is_rate
from hak.one.number.is_a import f as is_num
from hak.puvyz import f as puvyz

def f(u, v):
  if not is_rate(u): raise ValueError(f'u: {u} is not a rate')
  if not is_num(v): raise ValueError(f'v: {v} is not a number')
  return make_rate(u['numerator']*v, u['denominator'], u['unit'])

def t_a():
  u = make_rate(1, 3, {'a': 1})
  v = 1
  y = make_rate(1, 3, {'a': 1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_b():
  u = make_rate( 9, 7, {'b': 1})
  v = 5
  y = make_rate(45, 7, {'b': 1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_c():
  u = make_rate(1, 3, {'c': 1})
  v = 3
  y = make_rate(1, 1, {'c': 1})
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
