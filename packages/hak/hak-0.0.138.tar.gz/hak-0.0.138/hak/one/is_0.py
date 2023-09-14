from hak.pf import f as pf
from hak.pxyf import f as pxyf

# is_0
f = lambda x: f"{x}" == '0'
t_0 = lambda: pxyf(1, 0, f)
t_1 = lambda: pxyf(0, 1, f)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  return 1
