from hak.other.pip.version.to_str import f as make_v_str
from hak.one.string.contains.version import f as k
from hak.pxyz import f as pxyz
from hak.pf import f as pf

f = lambda version, lines: [
  (f"  version='{make_v_str(version)}'," if k(l) else l) for l in lines
]

v = {'major': 4, 'minor': 5, 'patch': 6}

def t_a():
  x = {'version': {}, 'lines': []}
  y = []
  z = f(**x)
  return pxyz(x, y, z)

def t_b():
  x = {'version': v, 'lines': []}
  y = []
  z = f(**x)
  return pxyz(x, y, z)

def t_c():
  x = {'version': v, 'lines': ["version = '1.2.3'\n", '.\n']}
  y = ["  version='4.5.6',", '.\n']
  z = f(**x)
  return pxyz(x, y, z)

def t_d():
  x = {'version': v, 'lines': ['.\n', "version = '1.2.3'\n"]}
  y = ['.\n', "  version='4.5.6',"]
  z = f(**x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  if not t_d(): return pf('!t_d')
  return True
