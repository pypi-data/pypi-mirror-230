from hak.one.string.filename.to_module_name import f as get_module_name
from hak.pf import f as pf
from hak.pxyz import f as pxyz

f = lambda x: sorted([get_module_name(x_i) for x_i in x])

def t_a():
  x = []
  y = []
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  x = ['./abc/xyz.py']
  y = ['abc.xyz']
  z = f(x)
  return pxyz(x, y, z)

def t_c():
  x = ['./abc/xyz.py', './abc/mno/xyz.py']
  y = ['abc.mno.xyz', 'abc.xyz']
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
