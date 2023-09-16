from hak.pxyz import f as pxyz
from hak.pf import f as pf

f = lambda x: 'version' in x

def t_true_a():
  x = 'xyz version'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_true_b():
  x = 'version'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_true_c():
  x = 'version xyz'
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false_a():
  x = 'xyz'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_b():
  x = ''
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true_a(): return pf('!t_true_a')
  if not t_true_b(): return pf('!t_true_b')
  if not t_true_c(): return pf('!t_true_c')
  if not t_false_a(): return pf('!t_false_a')
  if not t_false_b(): return pf('!t_false_b')
  return True
