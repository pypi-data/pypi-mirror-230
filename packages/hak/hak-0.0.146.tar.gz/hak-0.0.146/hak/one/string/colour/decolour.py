from hak.one.string.colour.bright.blue import f as bb
from hak.one.string.colour.bright.cyan import f as bc
from hak.one.string.colour.bright.green import f as bg
from hak.one.string.colour.bright.magenta import f as bm
from hak.one.string.colour.bright.red import f as br
from hak.one.string.colour.bright.white import f as bw
from hak.one.string.colour.bright.yellow import f as by
from hak.one.string.colour.dark.blue import f as db
from hak.one.string.colour.dark.cyan import f as dc
from hak.one.string.colour.dark.green import f as dg
from hak.one.string.colour.dark.magenta import f as dm
from hak.one.string.colour.dark.red import f as dr
from hak.one.string.colour.dark.white import f as dw
from hak.one.string.colour.dark.yellow import f as dy

from hak.pf import f as pf

# src.string.decolour
def f(x):
  for _ in [
    '\x1b[0;0m',
    '\x1b[0;31m',
    '\x1b[0;32m',
    '\x1b[0;33m',
    '\x1b[0;34m',
    '\x1b[0;35m',
    '\x1b[0;36m',
    '\x1b[0;37m',
    '\x1b[1;31m',
    '\x1b[1;32m',
    '\x1b[1;33m',
    '\x1b[1;34m',
    '\x1b[1;35m',
    '\x1b[1;36m',
    '\x1b[1;37m',
  ]:
    x = x.replace(_, '')
  return x

def t_bb():
  x = bb('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_bc():
  x = bc('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_bg():
  x = bg('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_bm():
  x = bm('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_br():
  x = br('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_bw():
  x = bw('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_by():
  x = by('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_db():
  x = db('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dc():
  x = dc('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dg():
  x = dg('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dm():
  x = dm('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dr():
  x = dr('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dw():
  x = dw('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t_dy():
  x = dy('abc')
  y = 'abc'
  z = f(x)
  return y == z or pf([f'x: {[x]}', f'y: {[y]}', f'z: {[z]}'])

def t():
  if not t_bb(): return pf('t_bb failed')
  if not t_bc(): return pf('t_bc failed')
  if not t_bg(): return pf('t_bg failed')
  if not t_bm(): return pf('t_bm failed')
  if not t_br(): return pf('t_br failed')
  if not t_bw(): return pf('t_bw failed')
  if not t_by(): return pf('t_by failed')
  if not t_db(): return pf('t_db failed')
  if not t_dc(): return pf('t_dc failed')
  if not t_dg(): return pf('t_dg failed')
  if not t_dm(): return pf('t_dm failed')
  if not t_dr(): return pf('t_dr failed')
  if not t_dw(): return pf('t_dw failed')
  if not t_dy(): return pf('t_dy failed')
  return True

if __name__ == '__main__': print(t())
