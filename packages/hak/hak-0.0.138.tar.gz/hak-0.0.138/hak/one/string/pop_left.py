from hak.pxyz import f as pxyz

f = lambda x: (x[1:], x[:1])

def t():
  x = 'abcd'
  y = ('bcd', 'a')
  z = f(x)
  return pxyz(x, y, z)
