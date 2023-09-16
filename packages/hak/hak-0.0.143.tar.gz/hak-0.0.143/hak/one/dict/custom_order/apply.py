from copy import deepcopy
from hak.pxyz import f as pxyz

# apply_custom_order
def f(x):
  order = deepcopy(x['order'])
  names = [n for n in x['names'] if n not in order]
  return order + names

def t():
  x = {'order': list('cba'), 'names': list('abcdef')}
  y = ['c', 'b', 'a', 'd', 'e', 'f']
  z = f(x)
  return pxyz(x, y, z)
