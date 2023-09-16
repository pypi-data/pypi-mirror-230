from hak.pxyz import f as pxyz

f = lambda x: sorted(list(set([k for d in x for k in d.keys()])))

def t():
  x = [
    {'a':  True, 'b':  True},
    {'a':  True, 'b': False},
    {'a': False, 'b': False},
    {'a': False, 'b':  True, 'c': None}
  ]
  y = ['a', 'b', 'c']
  z = f(x)
  return pxyz(x, y, z)
