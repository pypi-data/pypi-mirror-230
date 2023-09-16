from numbers import Number

from hak.pf import f as pf
from hak.pxyz import f as pxyz

f = lambda x: isinstance(x, Number)

def t_true_zero():
  x = 0
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_true_float():
  x = 0.1
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_true_complex():
  x = 0.1j + 5
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false_str():
  x = '0'
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_None():
  x = None
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true_zero(): return pf('!t_true_zero')
  if not t_true_float(): return pf('!t_true_float')
  if not t_true_complex(): return pf('!t_true_complex')
  if not t_false_str(): return pf('!t_false_str')
  if not t_false_None(): return pf('!t_false_None')
  return True
