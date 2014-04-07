from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shlex

from beast.env.ReadEnvFile import read_env_file
from beast.util.String import is_string

_BAD_VARS_ERROR = """
WARNING: the following variables appearing in %s were not understood:
  %s"""

def add_user_env(env, dotfile, print=print):
    df = os.path.expanduser(dotfile)
    try:
        with open(df, 'r') as f:
            dotvars = read_env_file(f.read())
    except IOError:
        if os.path.exists(df):
            print("WARNING: Dotfile %s exists but can't be read.")
        dotvars = {}

    bad_names = []
    for name, value in dotvars.items():
        if name in env:
            if is_string(env[name]):
                env[name] = value
            else:
                bad_names.append(name)
    if bad_names:
        print(_BAD_VARS_ERROR % (dotfile, '\n  '.join(bad_names)))

    for name, default in env.items():
        env[name] = os.environ.get(name, default)
