from hak.pf import f as pf
from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pxyz import f as pxyz

# increment
f = lambda x: mkfy({'final_year': x['final_year']+1})

def t_a():
  x = mkfy({'start_year': 2022})
  y = mkfy({'start_year': 2023})
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_a(): return pf('!t_a')
  return True
