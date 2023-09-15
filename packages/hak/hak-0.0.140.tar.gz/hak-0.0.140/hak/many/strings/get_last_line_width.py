# ignore_overlength_lines
from hak.one.string.char.last.find import f as find_last
from hak.pf import f as pf
from hak.pxyz import f as pxyz

# get_last_line_width
f = lambda x: (len(x) - find_last(x, '\n')) if '\n' in x else len(x)

def t_0():
  x = "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 10"
  y = 79
  z = f(x)
  return pxyz(x, y, z)

def t_1():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 10"
  ])
  y = 10
  z = f(x)
  return pxyz(x, y, z)

def t_2():
  x = "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10"
  y = 87
  z = f(x)
  return pxyz(x, y, z)

def t_3():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10"
  ])
  y = 18
  z = f(x)
  return pxyz(x, y, z)

def t_4():
  x = "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16"
  y = 141
  z = f(x)
  return pxyz(x, y, z)

def t_5():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16"
  ])
  y = 72
  z = f(x)
  return pxyz(x, y, z)

def t_6():
  x = "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17"
  y = 150
  z = f(x)
  return pxyz(x, y, z)

def t_7():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17"
  ])
  y = 81
  z = f(x)
  return pxyz(x, y, z)

def t_8():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,",
    "'r': 17"
  ])
  y = 10
  z = f(x)
  return pxyz(x, y, z)

def t_9():
  x = "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25"
  y = 222
  z = f(x)
  return pxyz(x, y, z)

def t_a():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25"
  ])
  y = 153
  z = f(x)
  return pxyz(x, y, z)

def t_b():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,",
    "'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25"
  ])
  y = 82
  z = f(x)
  return pxyz(x, y, z)

def t_c():
  x = '\n  '.join([
    "'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,",
    "'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,",
    "'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24,",
    "'z': 25"
  ])
  y = 10
  z = f(x)
  return pxyz(x, y, z)

def t():
  if not t_0(): return pf('!t_0')
  if not t_1(): return pf('!t_1')
  if not t_2(): return pf('!t_2')
  if not t_3(): return pf('!t_3')
  if not t_4(): return pf('!t_4')
  if not t_5(): return pf('!t_5')
  if not t_6(): return pf('!t_6')
  if not t_7(): return pf('!t_7')
  if not t_8(): return pf('!t_8')
  if not t_9(): return pf('!t_9')
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  if not t_c(): return pf('!t_c')
  return True
