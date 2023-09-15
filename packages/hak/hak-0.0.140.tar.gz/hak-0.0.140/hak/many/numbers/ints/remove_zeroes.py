from hak.pxyz import f as pxyz

f = lambda x: [_ for _ in x if _]

def t():
  x = [1, 0, 2, 0, 3]
  y = [1, 2, 3]
  z = f(x)
  return pxyz(x, y, z)
