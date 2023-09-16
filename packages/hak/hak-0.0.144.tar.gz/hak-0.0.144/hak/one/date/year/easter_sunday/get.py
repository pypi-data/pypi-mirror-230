from datetime import date

from hak.pf import f as pf
from hak.pxyz import f as pxyz

def f(year: int):
  g = year % 19
  c = year / 100
  h = (c - (c // 4) - int((8 * c + 13) / 25) + 19 * g + 15) % 30
  i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - g) // 11))
  day   = int(i - ((year + (year // 4) + i + 2 - c + (c // 4)) % 7) + 28)
  month = 4 if day > 31 else 3
  day = day if day <= 31 else day - 31

  return date(year, month, day)

def t_easter_2022():
  x = 2022
  y = date(2022, 4, 17)
  z = f(x)
  return pxyz(x, y, z)

def t_easter_2023():
  x = 2023
  y = date(2023, 4, 9)
  z = f(x)
  return pxyz(x, y, z)

def t_easter_2024():
  x = 2024
  y = date(2024, 3, 31)
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_easter_2022(): return pf('t_easter_2022')
  if not t_easter_2023(): return pf('t_easter_2023')
  if not t_easter_2024(): return pf('t_easter_2024')
  return True
