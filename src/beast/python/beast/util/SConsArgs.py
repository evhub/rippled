from __future__ import absolute_import, division, print_function, unicode_literals

def parse(arguments, defaults, print=print):
    results = dict(defaults)
    for name, value in arguments.items():
        if name in defaults:
            results[name] = value
        else:
            print("WARNING: don't understand argument %s=%s", (name, value))
    return results
