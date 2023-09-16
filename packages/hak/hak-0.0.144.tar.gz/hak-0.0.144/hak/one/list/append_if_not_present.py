from hak.pxyz import f as pxyz
from hak.pf import f as pf

def f(list, item_to_append):
  if item_to_append in list: return list
  return list + [item_to_append]

def t_appended():
  x = {
    'list': ['a', 'b', 'c'],
    'item_to_append': 'd'
  }
  y = ['a', 'b', 'c', 'd']
  z = f(**x)
  return pxyz(x, y, z)

def t_not_appended():
  x = {
    'list': ['a', 'b', 'c'],
    'item_to_append': 'b'
  }
  y = ['a', 'b', 'c']
  z = f(**x)
  return pxyz(x, y, z)

def t():
  if not t_appended(): return pf('!t_appended')
  if not t_not_appended(): return pf('!t_not_appended')
  return True
