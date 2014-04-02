from __future__ import absolute_import, division, print_function, unicode_literals

import os

def first_line_starting_with(filename, prefix):
  with open(filename, 'r') as contents:
    for line in contents:
      line = line.strip()
      if line.startswith(prefix):
        return line[len(prefix):].split()
  return []

def find_files_with_suffix(base, suffix):
    for parent, _, files in os.walk(base):
        for path in files:
            path = os.path.join(parent, path)
            if path.endswith(suffix):
                yield os.path.normpath(path)

def child_files(parent, files):
  return [os.path.normpath(os.path.join(parent, f)) for f in files]

def sibling_files(path, files):
  return child_files(os.path.dirname(path), files)

def replace_extension(file, ext):
  return os.path.splitext(file)[0] + ext
