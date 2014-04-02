from __future__ import absolute_import, division, print_function, unicode_literals

import os

LIBS_PREFIX = '// LIBS:'
MODS_PREFIX = '// MODULES:'

def first_line_starting_with(filename, prefix):
  with open(filename, 'r') as contents:
    for line in contents:
      line = line.strip()
      if line.startswith(prefix):
        return line[len(prefix):].split()
  return []

def get_libs(path):
    """Returns the list of libraries needed by the test source file. This is
       accomplished by scanning the source file for a special comment line
       with this format, which must match exactly:

       // LIBS: <name>...

       path = path to source file"""

    return first_line_starting_with(path, LIBS_PREFIX)

def get_source_modules(path):
    """Returns the list of source modules needed by the test source file.

     // MODULES: <module>...

     path = path to source file."""

    items = first_line_starting_with(path, MODS_PREFIX)
    parent = os.path.dirname(os.path.normpath(path))
    return [os.path.join(parent, i) for i in items]

def build_executable(env, path, main_program_file):
    """Build a stand alone executable that runs
       all the test suites in one source file."""
    libs = get_libs(path)
    source_modules = get_source_modules(path)
    bin = os.path.basename(os.path.splitext(path)[0])
    bin = os.path.join('bin', bin)
    srcs = [main_program_file, path] + (source_modules or [])

    # All paths get normalized here, so we can use posix
    # forward slashes for everything including on Windows
    srcs = [os.path.normpath(os.path.join('bin', x)) for x in srcs]
    objs = [os.path.splitext(x)[0] + '.o' for x in srcs]
    env_ = env
    if libs:
        env_.Append(LIBS=libs)
    env_.Program(bin, srcs)

def run_tests(env, main_program_file, root_dir, suffix):
    for root, dirs, files in os.walk(root_dir):
        for path in files:
            path = os.path.join(root, path)
            if path.endswith(suffix):
                build_executable(env, path, main_program_file)

