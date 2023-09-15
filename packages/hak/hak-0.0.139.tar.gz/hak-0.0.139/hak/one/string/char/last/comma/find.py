from hak.one.string.find_last_char import f as find_last_char
from hak.pxyz import f as pxyz

f = lambda x: find_last_char(x, ',')

def t():
  x = 'a,b,c,de'
  y = 5
  z = f(x)
  return pxyz(x, y, z)
