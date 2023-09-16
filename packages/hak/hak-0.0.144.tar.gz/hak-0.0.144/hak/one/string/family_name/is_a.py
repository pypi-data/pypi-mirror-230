from string import ascii_uppercase as _A_to_Z

def f(x):
  if x[:4] == 'den ': return True
  return all([isinstance(x, str), x[0] in _A_to_Z]) if len(x) else False

t = lambda: all([
  f('Forbes'),
  f('El Sawah'),
  f('den Hartog'),
  f('Hene Kankanamge'),
  not any([f(_) for _ in ['apple', '' ]])
])
