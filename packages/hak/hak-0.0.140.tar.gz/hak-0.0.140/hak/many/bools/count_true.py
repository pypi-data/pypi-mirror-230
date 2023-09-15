from hak.pxyz import f as pxyz
from hak.pf import f as pf
from random import randint as u

f = lambda x: len([_ for _ in x if _])

def t_a():
  n = u(0, 10)
  x = [*[True] * n, False]
  y = n
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  n = u(0, 10)
  x = [*[1]*n, 0, False]
  y = n
  z = f(x)
  return pxyz(x, y, z)

def t_c():
  x = []
  y = 0
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
