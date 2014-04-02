from __future__ import absolute_import, division, print_function, unicode_literals

def is_string(s):
  return isinstance(s, (str, unicode))

def join_items(items, joiner=''):
    return joiner.join(str(i) for i in items or ())

