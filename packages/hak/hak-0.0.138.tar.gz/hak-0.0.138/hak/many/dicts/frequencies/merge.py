from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(a, b):
  d_ab = {k_a: a[k_a] for k_a in a}
  for k_b in b:
    if k_b in d_ab:
      for k in b[k_b]:
        d_ab[k_b][k] = d_ab[k_b][k] + b[k_b][k] if k in d_ab[k_b] else b[k_b][k]
    else:
      d_ab[k_b] = b[k_b]
  return d_ab

def t_a():
  x = {
    'a': {'aa': {'a': 1, 'b': 2, '!': 3}, 'ab': {'a': 4, 'b': 5, '!': 6}},
    'b': {'ab': {'a': 7, 'b': 8, '!': 9}, 'ba': {'a': 1, 'b': 2, '!': 3}}
  }
  y = {
    'aa': {'a':  1, 'b':  2, '!':  3},
    'ab': {'a': 11, 'b': 13, '!': 15},
    'ba': {'a':  1, 'b':  2, '!':  3},
  }
  z = f(**x)
  return pxyz(x, y, z)

def t_b():
  x = {
    'a': {'aa': {'c': 2}},
    'b': {'aa': {'d': 1}}
  }
  y = {'aa': {'c': 2}, 'aa': {'c': 2, 'd': 1}}
  z = f(**x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  return True
