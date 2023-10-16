from hak.pf import f as pf
from hak.pxyz import f as pxyz
from string import digits

# src.string.date.separator.get
def f(x):
  d = {char: 0 for char in x if char not in digits}
  for char in x:
    if char not in digits:
      d[char] += 1
  
  for k in d:
    if d[k] == 2:
      return k

def t_0():
  x = '2022-11-11'
  y = '-'
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = '28/03/2022'
  y = '/'
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = '2022 01 31'
  y = ' '
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = '19 Nov 2021'
  y = ' '
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = '2022-05-06'
  y = '-'
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  return True
