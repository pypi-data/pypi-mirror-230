from hak.pxyz import f as pxyz

def f(x):
  observed = set()
  result = []
  for x_i in x:
    if x_i not in observed:
      observed.add(x_i)
      result.append(x_i)
  return result

def t():
  x = [0, 0, 0, 1, 1, 2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 10]
  y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]
  z = f(x)
  return pxyz(x, y, z)
