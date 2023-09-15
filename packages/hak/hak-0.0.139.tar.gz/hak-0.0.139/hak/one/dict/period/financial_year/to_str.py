from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pxyz import f as pxyz

# to_str
f = lambda x: f"{x['start_year']} - {x['final_year']}"

def t():
  x = mkfy({'start_year': 2022})
  y = '2022 - 2023'
  z = f(x)
  return pxyz(x, y, z)
