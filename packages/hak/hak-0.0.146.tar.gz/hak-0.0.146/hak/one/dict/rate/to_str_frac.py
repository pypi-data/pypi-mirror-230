from hak.one.dict.rate.make import f as rate
from hak.pxyf import f as pxyf
from hak.pf import f as pf

def f(x):
  if x['denominator'] == 0: return f"undefined"
  if x['numerator'] == 0: return f""
  if x['denominator'] == 1: return f"{x['numerator']}"
  return f"{x['numerator']}/{x['denominator']}"

t_a = lambda: pxyf(rate(710, 113, {'a': 1}), '710/113', f)
t_b = lambda: pxyf(rate(2, 1, {'a': 1}), '2', f)
t_c = lambda: pxyf(rate(0, 1, {'a': 1}), '', f)
t_d = lambda: pxyf(rate(1, 0, {'a': 1}), 'undefined', f)

def t():
  if not t_a(): return pf('t_a failed')
  if not t_b(): return pf('t_b failed')
  if not t_c(): return pf('t_c failed')
  if not t_d(): return pf('t_d failed')
  return 1
