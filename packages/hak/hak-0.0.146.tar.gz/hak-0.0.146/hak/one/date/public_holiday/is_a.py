from datetime import date
from datetime import timedelta as td

from hak.one.date.is_monday import f as is_monday
from hak.one.date.year.easter_sunday.get import f as get_easter_sunday
from hak.pf import f as pf
from hak.pxyz import f as pxyz

is_sunday = lambda δ: δ.weekday() == 6

def f(x):
  easter = get_easter_sunday(x.year)
  if x.month == 1 and x.day == 1: return True
  if all([is_sunday(x-td(1)), x.month == 1, x.day == 2]): return True
  if x.month == 1 and x.day == 26: return True
  if x.month == 3 and x.day == 13: return True
  if easter -td(2) == x: return True
  if easter -td(1) == x: return True
  if easter == x: return True
  if easter +td(1) == x: return True
  if x.month == 4 and x.day == 25: return True
  if all([x.month == 5, is_monday(x), x.day >= 27]): return True
  if all([x.month == 6, is_monday(x), 7 < x.day <= 14]): return True
  if all([x.month == 10, is_monday(x), x.day <= 7]): return True
  if all([x.month == 12, x.day == 25]): return True
  if all([x.month == 12, x.day == 26]): return True
  return False

def t_not_public_holiday_a():
  # Wednesday 25 January 2023
  x = date(2023, 1, 25)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_new_years_day_act():
  # Sunday 1 January 2023
  x = date(2023, 1, 1)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_new_years_day_obs():
  # Monday 2 January 2023
  x = date(2023, 1, 2)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_australia_day():
  # Australia Day	Thursday 26 January 2023
  x = date(2023, 1, 26)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_canberra_day():
  # Canberra Day	Monday 13 March 2023
  x = date(2023, 3, 13)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_good_friday():
  # Good Friday	Friday 7 April 2023
  x = date(2023, 4, 7)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_easter_saturday():
  # Easter Saturday – the day after Good Friday	Saturday 8 April 2023
  x = date(2023, 4, 8)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_easter_sunday():
  # Easter Sunday	Sunday 9 April 2023
  x = date(2023, 4, 9)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_easter_monday():
  # Easter Monday	Monday 10 April 2023
  x = date(2023, 4, 10)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_anzac_day():
  # ANZAC Day	Tuesday 25 April 2023
  x = date(2023, 4, 25)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_not_public_holiday_b():
  # Wednesday 28 May 2023
  x = date(2023, 5, 28)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_not_public_holiday_c():
  x = date(2023, 5, 22)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_reconciliation_day():
  # Reconciliation Day	Monday 29 May 2023**
  x = date(2023, 5, 29)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_not_public_holiday_d():
  x = date(2023, 6, 5)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_not_public_holiday_e():
  x = date(2023, 6, 19)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_sovereigns_birthday():
  # Sovereign's Birthday	Monday 12 June 2023
  x = date(2023, 6, 12)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_not_public_holiday_f():
  x = date(2023, 10, 9)
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_labour_day():
  # Labour Day	Monday 2 October 2023
  x = date(2023, 10, 2)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_christmas_day():
  # Christmas Day	Monday 25 December 2023
  x = date(2023, 12, 25)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_boxing_day():
  # Boxing Day	Tuesday 26 December 2023
  x = date(2023, 12, 26)
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_not_public_holiday_a(): return pf('t_not_public_holiday_a')
  if not t_new_years_day_act(): return pf('t_new_years_day_act failed')
  if not t_new_years_day_obs(): return pf('t_new_years_day_obs failed')
  if not t_australia_day(): return pf('t_australia_day failed')
  if not t_canberra_day(): return pf('t_canberra_day failed')
  if not t_good_friday(): return pf('t_good_friday failed')
  if not t_easter_saturday(): return pf('t_easter_saturday failed')
  if not t_easter_sunday(): return pf('t_easter_sunday failed')
  if not t_easter_monday(): return pf('t_easter_monday failed')
  if not t_anzac_day(): return pf('t_anzac_day failed')
  if not t_not_public_holiday_b(): return pf('t_not_public_holiday_b')
  if not t_not_public_holiday_c(): return pf('t_not_public_holiday_c')
  if not t_reconciliation_day(): return pf('t_reconciliation_day failed')
  if not t_not_public_holiday_d(): return pf('t_not_public_holiday_d')
  if not t_not_public_holiday_e(): return pf('t_not_public_holiday_e')
  if not t_sovereigns_birthday(): return pf('t_sovereigns_birthday failed')
  if not t_not_public_holiday_f(): return pf('t_not_public_holiday_f')
  if not t_labour_day(): return pf('t_labour_day failed')
  if not t_christmas_day(): return pf('t_christmas_day failed')
  if not t_boxing_day(): return pf('t_boxing_day failed')
  return True
