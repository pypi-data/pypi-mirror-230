from hak.pxyz import f as pxyz
from hak.pf import f as pf

f = lambda string, char: len(string) - len(string.replace(char, ''))

def t_a():
  x = {'string': 'a', 'char': ' ' }
  y = 0
  z = f(**x)
  return pxyz(x, y, z)

def t_b():
  x = {'string': 'a b', 'char': ' ' }
  y = 1
  z = f(**x)
  return pxyz(x, y, z)

def t_c():
  x = {'string': 'a b c', 'char': ' ' }
  y = 2
  z = f(**x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
