from hak.pxyz import f as pxyz

f = lambda string, char: len(string)-string[::-1].find(char)-1

def t():
  x = {'string': 'a,b,c,de', 'char': ','}
  y = 5
  z = f(**x)
  return pxyz(x, y, z)
