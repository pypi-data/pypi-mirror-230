from hak.puvyz import f as puvyz
from hak.pf import f as pf

def f(u, v):
  if u == v: return (True, 'Match')
  if len(u) < len(v): return (False, f'len(u): {len(u)} < len(v): {len(v)}')
  if len(u) > len(v): return (False, f'len(u): {len(u)} > len(v): {len(v)}')
  
  for i in range(len(u)):
    if u[i] != v[i]:
      return (False, f"x[{i}]: '{u[i]}' != y[{i}]: '{v[i]}'", i)
  
  return (False, "Unknown mismatch")
  
def t_match():
  u = 'abc'
  v = 'abc'
  y = (True, 'Match')
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_less():
  u = 'abc'
  v = 'abcd'
  y = (False, 'len(u): 3 < len(v): 4')
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_greater():
  u = 'abcd'
  v = 'abc'
  y = (False, 'len(u): 4 > len(v): 3')
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_not_equal():
  u = 'axc'
  v = 'ayc'
  y = (False, "x[1]: 'x' != y[1]: 'y'", 1)
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_match(): return pf('!t_match')
  if not t_less(): return pf('!t_less')
  if not t_greater(): return pf('!t_greater')
  if not t_not_equal(): return pf('!t_not_equal')
  return True
