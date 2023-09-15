# ignore_overlength_lines

from datetime import date

from .financial_year.get_end_date import f as f_fy
from .financial_year.make import f as mkfy
from .month.get_end_date import f as get_col_hor_line_from_records

from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_ω
f = lambda x: (get_col_hor_line_from_records if 'month' in x else f_fy)(x)

def t_fy():
  x = {'financial_year': mkfy({'start_year': 2022})}
  y = date(2023, 6, 30)
  z = f(x)
  return pxyz(x, y, z)

def t_0():
  x = {'month': {'year': 2016, 'number':  5}}
  y = date(2016,  5, 31)
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = {'month': {'year': 2017, 'number':  6}}
  y = date(2017,  6, 30)
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = {'month': {'year': 2020, 'number':  2}}
  y = date(2020,  2, 29)
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = {'month': {'year': 2021, 'number':  2}}
  y = date(2021,  2, 28)
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = {'month': {'year': 2021, 'number': 12}}
  y = date(2021, 12, 31)
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('!t_0')
  if not t_1(): return pf('!t_1')
  if not t_2(): return pf('!t_2')
  if not t_3(): return pf('!t_3')
  if not t_4(): return pf('!t_4')
  if not t_fy(): return pf('!t_fy')
  return True
