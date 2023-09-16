from hak.pxyz import f as pxyz

f = lambda string, char: [i for (i, c) in enumerate(string) if c == char]

def t():
  x = {'string': 'a,b,c,defg', 'char': ','}
  y = [1, 3, 5]
  z = f(**x)
  return pxyz(x, y, z)
