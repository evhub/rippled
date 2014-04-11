from __future__ import absolute_import, division, print_function, unicode_literals

from beast.platform import Platform
from beast.util import Dict
from beast.env import Tags

_DEFAULTS = {
    '': {
        'BOOST_HOME': None,
        'CC': 'gcc',
        'CCFLAGS': None,
        'CFLAGS': None,
        'CXX': 'g++',
        'CPPFLAGS': '-std=c++11 -frtti -fno-strict-aliasing',
        'CPPPATH': [],
        'LIBPATH': [],
        'LIBS': ['rt'],
        'LINKFLAGS': '',
    },

    'Darwin': {
        'CC': 'clang',
        'CXX': 'clang++',
        'CPPFLAGS': '-x c++ -stdlib=libc++ -std=c++11 -frtti',
        'LINKFLAGS': '-stdlib=libc++ -L/usr/local/opt/openssl/lib',
        'CXXFLAGS': '-I/usr/local/opt/openssl/include',
        'LIBS': ['z'],
     },

    'FreeBSD': {
        'CC': 'gcc46',
        'CXX': 'g++46',
        'CCFLAGS': '-Wl,-rpath=/usr/local/lib/gcc46',
        'LINKFLAGS': '-Wl,-rpath=/usr/local/lib/gcc46',
        'CPPFLAGS': '-DMDB_DSYNC=O_SYNC',
        'LIBS': ['kvm'],
    },

    # TODO: specific flags for Windows, Linux platforms.
}

TAGS = {
    'debug': {
        'CPPFLAGS': '-g -DDEBUG'
        },

    'nodebug': {
        'CPPFLAGS': '-DDEBUG'
        },

    'optimize': {
        'CPPFLAGS': '-O3',
        },

    'nooptimize': {
        'CPPFLAGS': '-O0',
        }
    }

def get_environment(arguments):
    tags = Tags.get_tags(arguments)
    env = Dict.compose_prefix_dicts(Platform.PLATFORM, _DEFAULTS)
    for tag in tags or []:
        for k, v in TAGS.get(tag, {}).items():
            env[k] = '%s %s' % (env[k], v)
    return env
