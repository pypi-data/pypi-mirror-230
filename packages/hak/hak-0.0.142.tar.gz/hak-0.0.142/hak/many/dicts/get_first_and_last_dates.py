from datetime import date
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_α_and_ω_dates_from_records
def f(x):
  dates = [item['date'] for item in x]
  return min(dates), max(dates)

def t_0():
  x = [
    {'date': date(2016, m, d), '...': '...'}
    for (m, d)
    in [(11, 14), (12, 25), (12, 31)]
  ]
  y = (date(2016,11,14), date(2016,12,31))
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('!t_0')
  return True
