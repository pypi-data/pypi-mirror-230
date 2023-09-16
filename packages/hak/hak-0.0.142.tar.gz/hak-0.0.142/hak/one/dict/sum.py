from hak.pxyf import f as pxyf
from hak.pf import f as pf
from hak.one.rate.rate import Rate as Q

f = lambda x: sum([f(x[k]) if isinstance(x[k], dict) else x[k] for k in x])

t_ints  = lambda: pxyf({'c': {'d': 2, 'e': 3, 'f': {'g': 4, 'h': 5}}},    14, f)
t_rates = lambda: pxyf({'b': Q(1), 'c': {'d': Q(2), 'e': Q(3)}},        Q(6), f)

def t():
  if not t_ints(): return pf('!t_ints')
  if not t_rates(): return pf('!t_rates')
  return 1
