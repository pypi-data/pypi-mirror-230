from datetime import date

from hak.one.bool.is_a import f as is_bool
from hak.one.date.is_a import f as is_date
from hak.one.dict.rate.is_a import f as is_rate
from hak.one.dict.rate.make import f as make_rate
from hak.one.number.complex.is_a import f as is_complex
from hak.one.number.float.is_a import f as is_float
from hak.one.number.int.is_a import f as is_int
from hak.one.string.is_a import f as is_str
from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(x):
  if is_str(x): return 'str'
  if is_bool(x): return 'bool'
  if is_int(x): return 'int'
  if is_float(x): return 'float'
  if is_complex(x): return 'complex'
  if is_date(x): return 'date'
  if is_rate(x): return 'rate'
  if x is None: return 'none'
  raise NotImplementedError(f'! This condition not yet considered; x: {x}')

def t_0():
  x = 'abc'
  y = 'str'
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = 1
  y = 'int'
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = 1.1
  y = 'float'
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = True
  y = 'bool'
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = 0+1j
  y = 'complex'
  z = f(x)
  return pxyz(x, y, z)

def t_6():
  x = date(2000, 1, 1)
  y = 'date'
  z = f(x)
  return pxyz(x, y, z)

def t_rate():
  x = make_rate(2000, 1, {'m': 1})
  y = 'rate'
  z = f(x)
  return pxyz(x, y, z)

def t_none():
  x = None
  y = 'none'
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  if not t_6(): return pf('t_6 failed')
  if not t_rate(): return pf('t_rate failed')
  if not t_none(): return pf('t_none failed')
  return True
