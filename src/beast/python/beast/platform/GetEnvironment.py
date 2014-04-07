from __future__ import absolute_import, division, print_function, unicode_literals

from beast.platform.Platform import PLATFORM

DEFAULTS = {
    '': {
        'BOOST_HOME': None,
        'CC': None,
        'CCFLAGS': None,
        'CFLAGS': None,
        'CPPFLAGS': None,
        'CXX': None,
        'CXXFLAGS': '-x c++ -stdlib=libc++ -std=c++11 -frtti -g',
        'DEBUG': None,
        'LIBPATH': '',
        'LIBS': '',
        'LINKFLAGS': '-stdlib=libc++',
        'OPTIMIZE': None,
        'RELEASE': True,
      },

    'Darwin': {
        'CC': 'clang',
        'CXX': 'clang++',
        'CXXFLAGS': '-x c++ -stdlib=libc++ -std=c++11 -frtti -g',
        'LINKFLAGS': '-stdlib=libc++',
    },
}
