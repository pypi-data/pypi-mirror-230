from hak.pf import f as pf
from hak.pxyf import f as pxyf

# is_none
f = lambda x: x is None
t_1 = lambda: pxyf(None, 1, f)
t_0 = lambda: pxyf(   0, 0, f)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  return 1
