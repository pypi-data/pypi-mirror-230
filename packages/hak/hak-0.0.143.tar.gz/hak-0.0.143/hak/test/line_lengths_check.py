from hak.many.strings.filepaths.py.testables.get import f as list_testables
from hak.one.file.load import f as load
from hak.pf import f as pf
from hak.one.string.colour.bright.red import f as danger
from hak.one.string.colour.bright.green import f as success

def f(_Pi=None):
  print('Checking line lengths...', end='\r')
  _Pi = list_testables() or _Pi
  for _pi in _Pi:
    ignore_line_lengths = False
    for line_index, line in enumerate(load(_pi).split('\n')):
      if 'ignore_overlength_lines' in line: ignore_line_lengths = True
      if len(line) > 80 and not ignore_line_lengths: return pf([
        '',
        f'{_pi}:{line_index+1}',
        danger(line)
      ])
  print(f"{success('PASS')} Line Lengths "+' '*20)

def t(): return True # TODO
