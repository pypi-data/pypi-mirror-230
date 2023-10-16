from hak.one.bool.random.make import f as make_bool
from hak.one.number.int.random.make import f as make_int
from hak.one.string.random.make import f as make_str
from hak.pf import f as pf
from hak.pxyz import f as pxyz

f = lambda x: type(x) == type(1j)

def t_false_int():
  x = make_int(1, 10)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_bool():
  x = make_bool()
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_str():
  x = make_str()
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_true():
  x = 0+2.5j
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true')
  if not t_false_int(): return pf('!t_false_int')
  if not t_false_bool(): return pf('!t_false_bool')
  if not t_false_str(): return pf('!t_false_str')
  return True
