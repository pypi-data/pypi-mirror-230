from hak.one.string.date.separator.get import f as get_separator
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# src.string.date_pieces.get
# get_bag
f = lambda x: set(x.split(get_separator(x)))

def t_0():
  x = '19 Nov 2021'
  y = set(['19', 'Nov', '2021'])
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = '2021-11-19'
  y = set(['2021', '11', '19'])
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = '28/03/2022'
  y = set(['2022', '03', '28'])
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  return True
