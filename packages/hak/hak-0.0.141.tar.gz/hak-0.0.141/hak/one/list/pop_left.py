from hak.pxyz import f as pxyz
from copy import deepcopy

f = lambda x: (x[1:], x[:1][0])

def t():
  x = ['a', 'b', 'c']
  y = ['b', 'c'], 'a'
  z = f(x)
  return pxyz(x, y, z)
