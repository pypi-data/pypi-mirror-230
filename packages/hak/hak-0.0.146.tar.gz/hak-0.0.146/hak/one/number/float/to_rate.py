from hak.pxyz import f as pxyz
from hak.pf import f as pf
from hak.one.dict.rate.make import f as make_rate

# float_to_rate
def f(x):
  d = 10**len(str(x).split('.')[1])
  return make_rate(round(x*d), d, {})

def t_true():
  x = 6.283185307179586
  y = {
    'numerator': 3141592653589793,
    'denominator': 500000000000000,
    'unit': {}
  }
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true')
  return True
