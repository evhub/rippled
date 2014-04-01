from __future__ import absolute_import, division, print_function, unicode_literals

BLUE = 94

def add_mode(text, *modes):
    modes = ';'.join(str(m) for m in modes)
    return '\033[%sm%s\033[0m' % (modes, text)

def blue(text):
    return add_mode(text, BLUE)

