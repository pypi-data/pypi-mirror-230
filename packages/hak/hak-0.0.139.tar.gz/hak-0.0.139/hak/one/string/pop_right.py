from hak.pxyz import f as pxyz

# def f(x): return (x[:len(x)-1], x[len(x)-1:])
f = lambda x: (x[:len(x)-1], x[len(x)-1:])

def t():
  x = 'abc'
  y = ('ab', 'c')
  z = f(x)
  return pxyz(x, y, z)
