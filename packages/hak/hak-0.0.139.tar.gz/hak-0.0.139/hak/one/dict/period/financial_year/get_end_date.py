from datetime import date

from hak.one.dict.period.financial_year.make import f as mkfy
from hak.pxyz import f as pxyz

# get_ω_date
f = lambda x: date(x['financial_year']['final_year'], 6, 30)

def t():
  x = {'financial_year': mkfy({'start_year': 2022})}
  y = date(2023, 6, 30)
  z = f(x)
  return pxyz(x, y, z)
