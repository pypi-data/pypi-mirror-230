from hak.pxyz import f as pxyz

# src.list.strings.get_index_of_first_difference
def f(x):
  u = x['u']
  v = x['v']
  for i in range(min(len(u), len(v))):
    if u[i] != v[i]:
      return i

def t():
  x = {'u': 'abcdefghijk', 'v': 'abcdefghiJk'}
  y = 9
  z = f(x)
  return pxyz(x, y, z)
