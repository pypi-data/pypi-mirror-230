from hak.pxyz import f as pxyz

f = lambda x: [k for k in x['names'] if k not in set(x['hidden'])]

def t():
  x = {'hidden': list('ace'), 'names': list('abcde')}
  y = list('bd')
  z = f(x)
  return pxyz(x, y, z)
