from hak.one.dict.is_a import f as is_dict
from hak.pf import f as pf
from hak.one.list.is_a import f as is_list
from hak.pxyz import f as pxyz

def f(x):
  if not is_dict(x): return False
  if 'header' not in x: return False
  if 'unit'   not in x: return False
  if 'values' not in x: return False
  if not is_list(x['values']): return False
  return True

def t_true():
  x = {
    'header': 'apples',
    'unit': '$/apple',
    'values': [0.25, 0.75]
  }
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false():
  x = None
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true')
  if not t_false(): return pf('!t_false')
  return True
