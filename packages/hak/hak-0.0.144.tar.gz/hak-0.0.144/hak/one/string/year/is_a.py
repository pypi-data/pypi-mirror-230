from hak.pxyz import f as pxyz

# src.string.year.is_a
# is_year
f = lambda x: len(x) == 4 and x.isdecimal()

def t():
  x = '2022'
  y = True
  z = f(x)
  return pxyz(x, y, z)
