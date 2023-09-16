from hak.puvyz import f as puvyz
from hak.one.dict.period.financial_year.make import f as mkfy

# gt
f = lambda u, v: u['start_year'] > v['start_year']

def t():
  u = mkfy({'start_year': 2023})
  v = mkfy({'final_year': 2023})
  y = True
  z = f(u, v)
  return puvyz(u, v, y, z)
