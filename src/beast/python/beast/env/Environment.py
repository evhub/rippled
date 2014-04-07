from __future__ import absolute_import, division, print_function, unicode_literals

import os

def fill_environment(
        env,
        appends=None,
        environment_variables=None,
        prepends=None,
        replacements=None,
        variant_directories=None,
        ):
    for name, path in (variant_directories or {}).items():
        env.VariantDir(os.path.join(*path), name, duplicate=0)

    for name, default in (environment_variables or {}).items():
        value = os.environ.get(name, default)
        if value:
            env[name] = value

    if replacements:
        env.Replace(**replacements)
    if prepends:
        env.Prepend(**prepends)
    if appends:
        env.Append(**appends)

