from hak.pxyz import f as pxyz

# src.list.ints.mode.get.py
def f(x):
  d = {}
  for x_i in x:
    if x_i not in d:
      d[x_i] = 0
    d[x_i] += 1

  max_so_far_value = -1
  max_so_far_key = None

  for k in d:
    if d[k] > max_so_far_value:
      max_so_far_key, max_so_far_value = k, d[k]

  return max_so_far_key

def t():
  x = [0, 0, 0, 1, 1, 1, 1, 2, 2]
  y = 1
  z = f(x)
  return pxyz(x, y, z)
