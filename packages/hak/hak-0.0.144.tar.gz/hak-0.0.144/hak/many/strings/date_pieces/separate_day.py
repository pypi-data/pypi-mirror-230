from hak.one.string.day.is_a import f as is_day
from hak.one.string.month.is_a import f as is_month
from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(x):
  a, b = x
  a_m = is_month(a)
  b_m = is_month(b)
  a_d = is_day(a)
  b_d = is_day(b)

  if       a_m and     b_m and     a_d and     b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!A')
    
  elif     a_m and     b_m and     a_d and not b_d: return int(a), set([b])
  elif     a_m and     b_m and not a_d and     b_d: return int(b), set([a])
  elif     a_m and     b_m and not a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!D')
    
  elif     a_m and not b_m and     a_d and     b_d: return int(b), set([a])
  elif     a_m and not b_m and     a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!F')
    
  elif     a_m and not b_m and not a_d and     b_d: return int(b), set([a])
  elif     a_m and not b_m and not a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!H')
    
  elif not a_m and     b_m and     a_d and     b_d: return int(a), set([b])
  elif not a_m and     b_m and     a_d and not b_d: return int(a), set([b])
  elif not a_m and     b_m and not a_d and     b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!K')
    
  elif not a_m and     b_m and not a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!L')
    
  elif not a_m and not b_m and     a_d and     b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!M')
    
  elif not a_m and not b_m and     a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!N')
    
  elif not a_m and not b_m and not a_d and     b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!O')
    
  elif not a_m and not b_m and not a_d and not b_d:
    pf([
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!P')
  
  else:
    pf([
      'This branch should be impossible',
      f'x: {x}',
      f'a: {a:>3} | {a_m:>1} | {a_d:>1}',
      f'b: {b:>3} | {b_m:>1} | {b_d:>1}',
      ''
    ])
    raise NotImplementedError('!P')

def t_0():
  x = set(['19', 'Nov'])
  y = 19, set(['Nov'])
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = set(['11', '19'])
  y = 19, set(['11'])
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = set(['03', '28'])
  y = 28, set(['03'])
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = set(['07', 'Jan'])
  y = 7, set(['Jan'])
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = set(['Jan', '07'])
  y = 7, set(['Jan'])
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  return True
