from hak.pxyz import f as pxyz

# convert_list_of_tuples_to_dict
def f(x):
  Δ = {k: 0 for (k, _) in x}
  for (k, v) in x: Δ[k] += v
  return Δ

def t():
  x = [('a', 1), ('b', 2), ('a', 3), ('b', 4)]
  y = {'a': 4, 'b': 6}
  z = f(x)
  return pxyz(x, y, z)
