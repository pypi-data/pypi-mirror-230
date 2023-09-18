# ignore_overlength_lines
from hak.pf import f as pf
from hak.many.strings.get_last_line_width import f as get_last_line_width
from hak.one.string.dict.to_limited_width_dict_string import f as dict_string_to_limited_width_dict_string
from hak.pxyz import f as pxyz

def _f(x, w):
  result = ', '.join([f"'{k}': {x[k]}" for k in x])
  while get_last_line_width(result) > w-2:
    result = dict_string_to_limited_width_dict_string(result)
  return result

def f(x, w=80):
  if len(str(x)) <= w: return str(x)
  return '{\n  '+_f(x, w)+'\n}'

def t_short():
  x = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8}
  y = "{'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8}"
  z = f(x)
  return pxyz(x, y, z)

def t_w():
  x = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9}
  y = "{'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9}"
  z = f(x)
  return pxyz(x, y, z)

def t_too_long_a():
  x = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 10}
  y = '\n'.join([
    "{",
    "  'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "  'j': 10",
    "}",
  ])
  z = f(x)
  return pxyz(x, y, z)

def t_too_long_b():
  x = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,
    'j': 9, 'k': 10
  }
  y = '\n'.join([
    "{",
    "  'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "  'j': 9, 'k': 10",
    "}",
  ])
  z = f(x)
  return pxyz(x, y, z)

def t_too_long_c():
  x = {chr(k+97): k for k in range(17)}
  y = '\n'.join([
    "{",
    "  'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "  'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16",
    "}",
  ])
  z = f(x)
  return pxyz(x, y, z)

def t_too_long_d():
  x = {chr(k+97): k for k in range(18)}
  y = '\n'.join([
    "{",
    "  'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "  'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,",
    "  'r': 17",
    "}",
  ])
  z = f(x)
  return pxyz(x, y, z)

def t_too_long_e():
  x = {chr(k+97): k for k in range(26)}
  y = '\n'.join([
    "{",
    "  'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "  'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,",
    "  'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24,",
    "  'z': 25",
    "}",
  ])
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_short(): return pf('t_short() failed')
  if not t_w(): return pf('t_w() failed')
  if not t_too_long_a(): return pf('t_too_long_a() failed')
  if not t_too_long_b(): return pf('t_too_long_b() failed')
  if not t_too_long_c(): return pf('t_too_long_c() failed')
  if not t_too_long_d(): return pf('t_too_long_d() failed')
  if not t_too_long_e(): return pf('t_too_long_e() failed')
  return True
