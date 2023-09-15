from hak.one.string.colour.bright.magenta import f as mg
from hak.one.string.colour.bright.cyan import f as cy
from hak.pf import f as pf
from hak.puvyz import f as puvyz

_f = lambda u_i, v_i, i: {'u_i': u_i, 'v_i': v_i, 'i': i}

def f(u, v):
  if u == v: return None
  if len(u) < len(v): return f(u, v[:len(u)]) or _f(None, v[len(u)], len(u))
  if len(u) > len(v): return f(u[:len(v)], v) or _f(u[len(v)], None, len(v))
  return [_f(u[i], v[i], i) for i in range(len(u)) if u[i] != v[i]][0]

def t_diff_strs_same_length():
  u = 'abcde'
  v = 'abxde'
  y = {'u_i': 'c', 'v_i': 'x', 'i': 2}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_matching_strs():
  u = 'abcde'
  v = 'abcde'
  y = None
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_isoprefiu_len_lt_v_len():
  u = 'abcd'
  v = 'abcdxfg'
  y = {'u_i': None, 'v_i': 'x', 'i': 4}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_isoprefiu_len_gt_v_len():
  u = 'abcdxfg'
  v = 'abcd'
  y = {'u_i': 'x', 'v_i': None, 'i': 4}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_diff_str_u_len_lt_v_len():
  u = 'abcd'
  v = 'axcdefg'
  y = {'u_i': 'b', 'v_i': 'x', 'i': 1}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t_diff_str_u_len_gt_v_len():
  u = 'axcdefg'
  v = 'abcd'
  y = {'u_i': 'x', 'v_i': 'b', 'i': 1}
  z = f(u, v)
  return puvyz(u, v, y, z)

def t():
  if not t_matching_strs(): return pf('!t_matching_strs')
  if not t_diff_strs_same_length(): return pf('!t_diff_strs_same_length')
  if not t_isoprefiu_len_lt_v_len(): return pf('!t_isoprefiu_len_lt_v_len')
  if not t_isoprefiu_len_gt_v_len(): return pf('!t_isoprefiu_len_gt_v_len')
  if not t_diff_str_u_len_lt_v_len(): return pf('!t_diff_str_u_len_lt_v_len')
  if not t_diff_str_u_len_gt_v_len(): return pf('!t_diff_str_u_len_gt_v_len')
  return True
