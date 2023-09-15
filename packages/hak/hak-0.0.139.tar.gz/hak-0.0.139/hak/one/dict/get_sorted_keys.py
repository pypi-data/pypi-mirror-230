from hak.pf import f as pf
from hak.pxyz import f as pxyz
from datetime import date
from hak.one.dict.is_a import f as is_dict

f = lambda x: sorted(x.keys()) if is_dict(x) else []

def t_valid():
  x = {'z': 0, 'y': 1, 'x': 2}
  y = ['x', 'y', 'z']
  z = f(x)
  return pxyz(x, y, z)

def t_date():
  x = date.today()
  y = []
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_valid(): return pf('t_valid failed')
  if not t_date(): return pf('t_date failed')
  return True
