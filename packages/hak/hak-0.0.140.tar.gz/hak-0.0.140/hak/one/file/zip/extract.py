from zipfile import ZipFile
from hak.one.directory.make import f as mkdirine
from hak.one.directory.remove import f as rmdirie
from hak.one.file.load import f as load

_dir = './temp_file_zip_extract'

up = lambda: mkdirine(_dir)
dn = lambda: rmdirie(_dir)

def f(source, destination):
  with ZipFile(source, 'r') as _f: _f.extractall(destination)

def t():
  up()
  f('./hak/one/file/zip/test_data.zip', _dir)
  y = load('./hak/one/file/zip/test_y.txt')
  z = load(f'{_dir}/pi.txt')
  dn()
  return y == z
