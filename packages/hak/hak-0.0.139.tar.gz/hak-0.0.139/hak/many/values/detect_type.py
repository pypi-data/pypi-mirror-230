from datetime import date
from datetime import datetime
from hak.one.bool.is_a import f as is_bool
from hak.one.date.is_a import f as is_date
from hak.one.datetime.is_a import f as is_datetime
from hak.one.dict.is_a import f as is_dict
from hak.one.number.float.is_a import f as is_float
from hak.one.number.int.is_a import f as is_int
from hak.one.set.is_a import f as is_set
from hak.one.string.is_a import f as is_str
from hak.one.tuple.is_a import f as is_tup
from hak.pf import f as pf
from hak.pxyz import f as pxyz
from hak.one.dict.rate.is_a import f as is_rate
from hak.one.dict.rate.make import f as make_rate

def f(x):
  if all([is_bool(x_i) for x_i in x]): return 'bool'
  if all([is_datetime(x_i) for x_i in x]): return 'datetime'
  if all([is_date(x_i) for x_i in x]): return 'date'
  if all([is_rate(x_i) for x_i in x]): return 'rate'
  if all([is_dict(x_i) for x_i in x]): return 'dict'
  if all([is_float(x_i) for x_i in x]): return 'float'
  if all([is_int(x_i) for x_i in x]): return 'int'
  if all([is_set(x_i) for x_i in x]): return 'set'
  if all([is_str(x_i) for x_i in x]): return 'str'
  if all([is_tup(x_i) for x_i in x]): return 'tup'
  return '?'

def t_bool():
  x = [True, False, False]
  y = 'bool'
  z = f(x)
  return pxyz(x, y, z)

def t_date():
  x = [date(2023, 1, 1), date(2023, 6, 30), date(2023, 12, 31)]
  y = 'date'
  z = f(x)
  return pxyz(x, y, z)

def t_datetime():
  x = [datetime(2023, 1, 1), datetime(2023, 6, 30), datetime(2023, 12, 31)]
  y = 'datetime'
  z = f(x)
  return pxyz(x, y, z)

def t_dict():
  x = [{0: 0}, {1: 1}, {2: 2}]
  y = 'dict'
  z = f(x)
  return pxyz(x, y, z)

def t_float():
  x = [0.0, 1.0, 2.0]
  y = 'float'
  z = f(x)
  return pxyz(x, y, z)

def t_int():
  x = [0, 1, 2]
  y = 'int'
  z = f(x)
  return pxyz(x, y, z)

def t_set():
  x = [set(), set('abc'), {'d', 'e', 'f'}]
  y = 'set'
  z = f(x)
  return pxyz(x, y, z)

def t_str():
  x = ['abc', 'ghi', 'jkl']
  y = 'str'
  z = f(x)
  return pxyz(x, y, z)

def t_tup():
  x = [('abc', 'ghi'), ('ghi', 'jkl')]
  y = 'tup'
  z = f(x)
  return pxyz(x, y, z)

def t_rate():
  x = [make_rate(1, 2, {'$': 1, 'm': -1}), make_rate(2, 3, {'m': 1, '$': -1})]
  y = 'rate'
  z = f(x)
  return pxyz(x, y, z)

def t_unknown():
  class A:
    def __init__(self):
      self.v = '...'
  x = [A(), A(), A()]
  y = '?'
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_unknown(): return pf('!t_unknown')
  if not t_bool(): return pf('!t_bool')
  if not t_date(): return pf('!t_date')
  if not t_datetime(): return pf('!t_datetime')
  if not t_dict(): return pf('!t_dict')
  if not t_float(): return pf('!t_float')
  if not t_int(): return pf('!t_int')
  if not t_set(): return pf('!t_set')
  if not t_str(): return pf('!t_str')
  if not t_tup(): return pf('!t_tup')
  if not t_rate(): return pf('!t_rate')
  return True
