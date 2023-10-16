from hak.pxyz import f as pxyz

f = lambda list, key: sorted(list, key=lambda d: d[key])

def t():
  x = {
    'list': [{'a': 1, 'z': 1}, {'a': 2, 'z': 0}, {'a': 0, 'z': 2}],
    'key': 'a'
  }
  y = [{'a': 0, 'z': 2}, {'a': 1, 'z': 1}, {'a': 2, 'z': 0}]
  z = f(**x)
  return pxyz(x, y, z)
