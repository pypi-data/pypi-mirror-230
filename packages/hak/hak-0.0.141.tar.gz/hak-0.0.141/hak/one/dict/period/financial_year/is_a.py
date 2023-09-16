from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(x):
  if 'start_year' not in x: return False
  if 'final_year' not in x: return False
  if x['final_year'] - x['start_year'] != 1: return False
  if len(x) != 2: return False
  return True

def t_true():
  x = {'start_year': 2022, 'final_year': 2023}
  y = True
  z = f(x)
  return pxyz(x, y, z)

def t_false_missing_start_year():
  x = {'final_year': 2024}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_missing_final_year():
  x = {'start_year': 2022}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_years_too_far():
  x = {'start_year': 2022, 'final_year': 2024}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_years_same():
  x = {'start_year': 2022, 'final_year': 2022}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t_false_has_extra_k():
  x = {'start_year': 2022, 'final_year': 2023, 'extra_key': None}
  y = False
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_true(): return pf('!t_true')
  if not t_false_missing_start_year(): return pf('!t_false_missing_start_year')
  if not t_false_missing_final_year(): return pf('!t_false_missing_final_year')
  if not t_false_years_too_far(): return pf('!t_false_years_too_far')
  if not t_false_years_same(): return pf('!t_false_years_same')
  if not t_false_has_extra_k(): return pf('!t_false_has_extra_k')
  return True
