from __future__ import absolute_import, division, print_function, unicode_literals

import os

def find_files_with_suffix(base, suffix):
    for parent, _, files in os.walk(base):
        for path in files:
            path = os.path.join(parent, path)
            if path.endswith(suffix):
                yield path


