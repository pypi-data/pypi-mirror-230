from hak.pf import f as pf

f = lambda if_true, condition, if_false: if_true if condition else if_false

t_true = lambda: f('a', True, 'b') == 'a'

t_false = lambda: f('a', False, 'b') == 'b'

def t():
  if not t_true(): return pf('t_true failed')
  if not t_false(): return pf('t_false failed')
  return True
