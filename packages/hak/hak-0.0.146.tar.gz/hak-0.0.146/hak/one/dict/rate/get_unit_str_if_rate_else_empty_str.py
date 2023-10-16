from hak.one.dict.get_or_default import f as get_or_default
from hak.one.dict.rate.is_a import f as is_rate
from hak.pf import f as pf
from hak.one.dict.unit.to_str import f as to_str
from hak.pxyz import f as pxyz

# get_unit
def f(k, record):
  v = get_or_default(record, k, {})
  return to_str(v['unit']) if is_rate(v) else ''

def t_a():
  x = {
    'k': 'a',
    'record': {
      'a': {'numerator': 2, 'denominator': 1, 'unit': {'m': 1}},
      'b': {'numerator': 3, 'denominator': 1, 'unit': {'$': 1}}
    }
  }
  y = 'm'
  z = f(**x)
  return pxyz(x, y, z)

def t_b():
  x = {
    'k': 'b',
    'record': {
      'a': {'...': 2, 'denominator': 1, 'unit': {}},
      'b': {'numerator': 3, 'denominator': 2, 'unit': {'$': 1, 'm': -1}}
    }
  }
  y = '$/m'
  z = f(**x)
  return pxyz(x, y, z)

record = {
  'description': 'Exchanged 1000 AUD for 100 USD',
  'flow_AUD': -1000.0,
  'flow_USD': 100.0,
  'flag_asset_aud_cash': -1,
  'flag_asset_usd_cash_as_aud': 1
}

def t():
  if not t_a(): return pf('!t_a')
  if not t_b(): return pf('!t_b')
  return True
