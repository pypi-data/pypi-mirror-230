from datetime import date

from hak.many.strings.date_pieces.get import f as get_bag
from hak.many.strings.date_pieces.separate_day import f as separate_day
from hak.many.strings.date_pieces.separate_year import f as separate_year
from hak.one.string.date.separator.get import f as get_separator
from hak.one.string.month.to_number import f as to_number
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# src.string.to_date
def f(x, date_string_format=None):
  if not date_string_format:
    bag = get_bag(x)
    if len(bag) != 3: raise NotImplementedError('!E: len(bag) != 3')
    year, bag = separate_year(bag)
    day, bag = separate_day(bag)
    month = to_number(bag.pop())
    return date(year, month, day)
  
  _ymd = x.split(get_separator(x))

  return date(*[int(_) for _ in [
    _ymd[date_string_format['year_index']],
    _ymd[date_string_format['month_index']],
    _ymd[date_string_format['day_index']]
  ]])

def t_0():
  x = '19 Nov 2021'
  y = date(2021, 11, 19)
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = '2021-11-19'
  y = date(2021, 11, 19)
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = '28/03/2022'
  y = date(2022, 3, 28)
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = '5/04/2022'
  x_date_string_format = {'year_index': 2, 'month_index': 1, 'day_index': 0}
  y = date(2022, 4, 5)
  z = f(x, x_date_string_format)
  return pxyz(x, y, z)

def t_4():
  x = '2022-05-06'
  x_date_string_format = {'year_index': 0, 'month_index': 1, 'day_index': 2}
  y = date(2022, 5, 6)
  z = f(x, x_date_string_format)
  return pxyz(x, y, z)

t_5 = lambda: f('2016-11-14') == date(2016, 11, 14)

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  if not t_5(): return pf('t_5 failed')
  return True
