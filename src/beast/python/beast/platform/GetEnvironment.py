from __future__ import absolute_import, division, print_function, unicode_literals

from beast.platform import Platform
from beast.util import Dict

_DEFAULTS = {
    '': {
        'BOOST_HOME': None,
        'CC': 'gcc',
        'CCFLAGS': None,
        'CFLAGS': None,
        'CXX': 'g++',
        'CPPFLAGS': '-std=c++11 -frtti -fno-strict-aliasing',
        'DEBUG': None,
        'LIBPATH': '',
        'LIBS': '',
        'LINKFLAGS': '',
        'OPTIMIZE': None,
        'RELEASE': True,
    },

    'Darwin': {
        'CC': 'clang',
        'CXXP': 'clang++',
        'CPPFLAGS': '-x c++ -stdlib=libc++ -std=c++11 -frtti',
        'LINKFLAGS': '-stdlib=libc++',
     },

    # TODO: specifics for Windows, and for Linux platforms.
}

TAGS = {
    'DEBUG': {
        'CXXFLAGS': '-g'
        },

    'OPTIMIZE': {
        'CXXFLAGS': '-O3',
        },

    'NOOPTIMIZE': {
        'CXXFLAGS': '-O0',
        }
    }

def get_environment(tags):
    env = Dict.compose_prefix_dicts(Platform.PLATFORM, _DEFAULTS)
    for tag in tags or []:
        for k, v in TAGS.get(tag, {}).items():
            env[k] = '%s %s' % (env[k], v)
    return env
