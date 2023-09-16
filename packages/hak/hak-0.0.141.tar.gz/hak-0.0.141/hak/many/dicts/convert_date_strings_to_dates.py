from copy import deepcopy
from datetime import date
from hak.many.strings.dates.detect_format import f as detect_format
from hak.one.string.date.to_date import f as str_to_date
from hak.pxyz import f as pxyz

# convert_date_strs_to_date
def f(x):
  date_string_format = detect_format([x_i['date'] for x_i in x])
  y = []
  for x_i in x:
    w = deepcopy(x_i)
    w['date'] = str_to_date(x_i['date'], date_string_format)
    y.append(w)
  return y

def t():
  x = [
    {'date': '2021-11-04', 'other': 'aaa'},
    {'date': '2021-11-19', 'other': 'bbb'},
    {'date': '2022-01-31', 'other': 'ccc'},
  ]
  y = [
    {'date': date(2021, 11,  4), 'other': 'aaa'},
    {'date': date(2021, 11, 19), 'other': 'bbb'},
    {'date': date(2022,  1, 31), 'other': 'ccc'},
  ]
  z = f(x)
  return pxyz(x, y, z)
