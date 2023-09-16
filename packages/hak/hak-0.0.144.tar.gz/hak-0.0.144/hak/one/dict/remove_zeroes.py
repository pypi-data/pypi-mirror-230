from hak.one.dict.rate.is_a import f as is_rate
from hak.one.dict.rate.make import f as make_rate
from hak.one.dict.rate.to_float import f as rate_to_float
from hak.pf import f as pf
from hak.pxyz import f as pxyz

f = lambda x: {
  k: x[k]
  for k
  in x
  if (rate_to_float(x[k]) if is_rate(x[k]) else x[k]) != 0
}

def t_0():
  x = {'a': 0, 'b': 1}
  y = {'b': 1}
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = {'a': 0, 'b': 1, 'rate_a': make_rate(1, 2, {})}
  y = {'b': 1, 'rate_a': make_rate(1, 2, {})}
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = {'a': 0, 'b': 1, 'rate_a': make_rate(0, 2, {})}
  y = {'b': 1}
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  return True
