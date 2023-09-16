from hak.pf import f as pf

# get_empty_fields
def f(x):
  all_keys = set([k for x_i in x for k in x_i])
  keys_with_values = set([])

  for x_i in x:
    for k in x_i:
      if not any([x_i[k] is None, x_i[k] == 0, x_i[k] == '']):
        keys_with_values.add(k)
        # keys.remove(k)
 
  return all_keys - keys_with_values

def t_0():
  x = [{}, {}]
  y = set([])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t_1():
  x = [{'a': 'a'}, {'b': 'b'}]
  y = set([])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t_2():
  x = [{'a': None}, {'b': 'b'}]
  y = set(['a'])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t_3():
  x = [{'a': None}, {'b': 'b'}, {'c': 0}]
  y = set(['a', 'c'])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t_3():
  x = [{'a': None}, {'b': 'b'}, {'c': 0}, {'d': ''}]
  y = set(['a', 'c', 'd'])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t_4():
  x = [{'a': None}, {'b': 'b'}, {'c': 0}, {'d': ''}, {'d': '!'}]
  y = set(['a', 'c'])
  z = f(x)
  return y == z or pf([f'x: {x}', f'y:\n{y}', f'z:\n{z}'])

def t():
  if not t_0(): return pf('t_0 failed')
  if not t_1(): return pf('t_1 failed')
  if not t_2(): return pf('t_2 failed')
  if not t_3(): return pf('t_3 failed')
  if not t_4(): return pf('t_4 failed')
  return True
