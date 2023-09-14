from requests import get
from hak.one.file.pickle.load_if_exists import f as load
from hak.one.dict.make_from_key_value_lists import f as make_from_key_val_lists
from hak.pxyz import f as pxyz

def f(name, response=None):
  response = response or get(f"https://pypi.org/project/{name}/")
  lines = [l for l in response.text.split('\n') if all([
    '<h2>Initiate a new hak project</h2>' not in l,
    'hak ' in l,
    'title' not in l
  ])]
  v_line = lines[0] if lines else '0.0.4'
  v_str = v_line.split('hak ')[-1]
  return make_from_key_val_lists(
    ['major', 'minor', 'patch'],
    [int(_) for _ in v_str.split('.')]
  )

def t():
  x = {
    'name': "hak",
    'response': load('./hak/other/pip/version/test_response.pkl')
  }
  y = {'major': 0, 'minor': 0, 'patch': 4}
  z = f(**x) 
  return pxyz(x, y, z)
