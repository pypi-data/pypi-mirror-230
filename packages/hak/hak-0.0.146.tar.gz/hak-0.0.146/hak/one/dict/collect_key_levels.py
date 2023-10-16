from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(x):
  result = _f({'': x}, -1, {})
  del result[-1]
  return result

def _f(x, level, result):
  for k in x:
    if level not in result:
      result[level] = set()
    result[level] |= set([k])
    result[level] |= _f(x[k], level+1, result)[level]
  return result

def t_a():
  x = {'k': {'u': {}, 'b': {}}, 'm': {}}
  y = {0: {'k', 'm'},1: {'u', 'b'}}
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  x = {'k': {'p': {'s': {}, 'l': {}}, 'k': {}}, 'n': {}}
  y = {0: {'k', 'n'}, 1: {'p', 'k'}, 2: {'l', 's'}}
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  return True
