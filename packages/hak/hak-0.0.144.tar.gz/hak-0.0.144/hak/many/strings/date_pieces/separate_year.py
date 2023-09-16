from hak.pf import f as pf
from hak.one.string.year.is_a import f as is_year
from hak.pxyz import f as pxyz

# src.set.date_pieces.separate_year
# separate_year_from_bag
def f(x):
  year = None
  new_bag = set([])
  for item in x:
    if is_year(item):
      year = int(item)
    else:
      new_bag.add(item)
  return year, new_bag

def t_0():
  x = set(['19', 'Nov', '2021'])
  y = 2021, set(['19', 'Nov'])
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = set(['2021', '11', '19'])
  y = 2021, set(['11', '19'])
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = set(['2022', '03', '28'])
  y = 2022, set(['03', '28'])
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  return True
