from __future__ import absolute_import, division, print_function, unicode_literals

import os

BOOST_HOME = 'BOOST_HOME'

def boost_path():
    try:
      path = os.environ[BOOST_HOME]
      if path:
        return path
    except KeyError:
      pass
    raise KeyError('%s environment variable is not set.' % BOOST_HOME)
