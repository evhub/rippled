from __future__ import absolute_import, division, print_function, unicode_literals

def is_string(s):
    """Is s a string? - in either Python 2.x or 3.x."""
    return isinstance(s, (str, unicode))

def join(items, joiner=''):
    """If items is not a string, stringify its members and join them."""
    if not items or is_string(items):
        return items or ''
    else:
        return joiner.join(str(i) for i in items)

