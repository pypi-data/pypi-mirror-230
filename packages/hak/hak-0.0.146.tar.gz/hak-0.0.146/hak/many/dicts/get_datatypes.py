from hak.many.dicts.get_all_keys import f as get_field_names
from hak.many.values.get_datatype import f as detect_datatype_from_values
from hak.one.dict.rate.make import f as make_rate
from hak.pxyz import f as pxyz

# src.table.fields.datatypes.get
f = lambda x: {
  k: detect_datatype_from_values([d[k] if k in d else None for d in x])
  for k in get_field_names(x)
}

def t():
  x = [
    {'a': True,  'b': 'abc', 'c': make_rate(1.23, 1, {'m': 1})},
    {'a': True,  'b': 'def', 'c': make_rate(1.23, 1, {'m': 1})},
    {'a': False, 'b': 'ghi', 'c': make_rate(1.23, 1, {'m': 1})},
  ]
  y = {'a': 'bool', 'b': 'str', 'c': 'rate'}
  z = f(x)
  return pxyz(x, y, z)
