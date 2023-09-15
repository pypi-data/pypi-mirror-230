from hak.pxyz import f as pxyz
from hak.one.dict.is_a import f as is_dict

def f(d, s=set()):
  for k in d:
    if is_dict(d[k]):
      s |= f(d[k], s)
  return s | set(d.keys())

def t():
  x =  {
    'a': {'aa': {'aaa': 'Lollipop'}, 'ab': None},
    'b': {'ba': None}
  }
  y = set(['a', 'aa', 'ab', 'aaa', 'b', 'ba'])
  z = f(x)
  return pxyz(x, y, z)
