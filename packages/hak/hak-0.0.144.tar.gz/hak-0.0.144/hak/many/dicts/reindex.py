from hak.pxyz import f as pxyz

def f(dicts, index_name):
  for index, item in enumerate(dicts): item[index_name] = index
  return dicts

def t():
  x = {
    'dicts': [{'i': 9, 'z': 2}, {'i': 0, 'z': 1}, {'i': 5, 'z': 0}],
    'index_name': 'i'
  }
  y = [{'i': 0, 'z': 2}, {'i': 1, 'z': 1}, {'i': 2, 'z': 0}]
  z = f(**x)
  return pxyz(x, y, z)
