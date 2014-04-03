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

def single_line(line, report_errors=True, joiner='+'):
    """Force a string to be a single line with no carriage returns, and report
    a warning if there was more than one line."""
    lines = line.strip().splitlines()
    if report_errors and len(lines) > 1:
        print('multiline result:', lines)
    return joiner.join(lines)
