from hak.pxyz import f as pxyz
from hak.pf import f as pf

s = [
  '\u2070', '\u00B9', '\u00B2', '\u00B3', '\u2074',
  '\u2075', '\u2076', '\u2077', '\u2078', '\u2079',
]

def _f_side(x):
  z = ''
  for k in sorted(x):
    z += f'{k}' if len(k) > 1 else f'{k}'
    if x[k] == 1: return z
    z += ''.join([s[int(j)] for j in str(x[k])])
  return z

def f(x):
  left = _f_side({k: x[k] for k in x if x[k] > 0})
  right = _f_side({k: -x[k] for k in x if x[k] < 0})
  if right:
    left = left or '1'
    return left+'/'+right
  return left

def t_m_1():
  x = {'m': 1}
  y = 'm'
  z = f(x)
  return pxyz(x, y, z)

def t_m_2():
  x = {'m': 2}
  y = 'm\u00B2'
  z = f(x)
  return pxyz(x, y, z)

def t_m_10():
  x = {'m': 10}
  y = 'm\u00B9\u2070'
  z = f(x)
  return pxyz(x, y, z)

def t_m_20():
  x = {'m': 20}
  y = 'm\u00B2\u2070'
  z = f(x)
  return pxyz(x, y, z)

def t_m_neg_1():
  x = {'m': -1}
  y = '1/m'
  z = f(x)
  return pxyz(x, y, z)

def t_dollar_per_square_metre():
  x = {'$': 1, 'm': -2}
  y = '$/m\u00B2'
  z = f(x)
  return pxyz(x, y, z)

def t_m_3():
  x = {'m': 3}
  y = 'm\u00B3'
  z = f(x)
  return pxyz(x, y, z)

def t_USD_per_AUD():
  x = {'USD': 1, 'AUD': -1}
  y = 'USD/AUD'
  z = f(x)
  return pxyz(x, y, z)

def t_USD_2_per_AUD():
  x = {'USD': 2, 'AUD': -1}
  y = 'USD\u00B2/AUD'
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_m_1(): return pf('!t_m_1')
  if not t_m_2(): return pf('!t_m_2')
  if not t_m_10(): return pf('!t_m_10')
  if not t_m_20(): return pf('!t_m_20')
  if not t_m_neg_1(): return pf('!t_m_neg_1')
  if not t_dollar_per_square_metre(): return pf('!t_dollar_per_square_metre')
  if not t_m_3(): return pf('!t_m_3')
  if not t_USD_per_AUD(): return pf('!t_USD_per_AUD')
  if not t_USD_2_per_AUD(): return pf('!t_USD_2_per_AUD')
  return True
