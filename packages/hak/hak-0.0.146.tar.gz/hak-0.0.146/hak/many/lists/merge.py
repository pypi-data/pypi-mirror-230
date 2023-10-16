from hak.pxyz import f as pxyz
from hak.pf import f as pf

f = lambda a, b: a + [b_i for b_i in b if b_i not in set(a)]

def t_a():
  x = {'a': [], 'b': []}
  y = []
  z = f(**x)
  return pxyz(x, y, z)

def t_b():
  x = {'a': list('abc'), 'b': list('def')}
  y = list('abcdef')
  z = f(**x)
  return pxyz(x, y, z)

def t_c():
  x = {'a': list('abc'), 'b': list('bcd')}
  y = list('abcd')
  z = f(**x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
