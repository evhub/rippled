from __future__ import absolute_import, division, print_function, unicode_literals

import curses

CAN_CHANGE_COLOR = True

# See https://en.wikipedia.org/wiki/ANSI_escape_code

RED = 91
GREEN = 92
BLUE = 94

def add_mode(text, *modes):
    if CAN_CHANGE_COLOR:
        modes = ';'.join(str(m) for m in modes)
        return '\033[%sm%s\033[0m' % (modes, text)
    else:
        return text

def blue(text):
    return add_mode(text, BLUE)

def green(text):
    return add_mode(text, GREEN)

def red(text):
    return add_mode(text, RED)

def warn(text, print=print):
    print('%s %s' % (red('WARNING:'), text))
