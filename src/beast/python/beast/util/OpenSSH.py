from __future__ import absolute_import, division, print_function, unicode_literals

import re

from beast.util import Iter

REQUIRED_VERSION = '1.0.1'
MATCH_VERSION = re.compile(r'#define\s+OPENSSL_VERSION_NUMBER\s+(\S+)')
DEFAULT_SSH_FILE = '/usr/include/openssl/opensslv.h'

DISABLED = True

def parse_version_number(version):
    try:
        ox = version[:2]
        assert ox.lower() == '0x'
        major = int(version[2], 16)
        minor = int(version[3:5], 16)
        fix = int(version[5:7], 16)
        patch = int(version[7:9], 16)
        status = version[9]
        assert status == 'f'

        patch = chr(patch + ord('a') - 1) if patch else ''
        return [major, minor, fix, patch]
    except:
        raise Exception("Can't understand version string " + version)

def get_version(filename=DEFAULT_SSH_FILE):
    try:
        with open(filename, 'r') as f:
            version = Iter.first(MATCH_VERSION.match, f).group(1)
        return parse_version_number(version)
    except:
        raise Exception("Can't find OpenSSH version number from file " + fname)

def split_version_string(version):
    try:
        parts = version.split('.')
        assert len(parts) == 3
        fix_patch = parts[2]
        patch = fix_patch[-1]
        if patch.isalpha():
            parts[2] = fix_patch[:-1]
        else:
            patch = ''
        parts.append(patch)
        for i in range(3):
            parts[i] = ord(parts[i]) - ord('0')
        return parts

    except:
        raise Exception("Can't understand version string " + version)

def to_string(version):
    return '.'.join(str(s) for s in version[:-1]) + version[-1]

def validate_version(required_version=REQUIRED_VERSION, filename=DEFAULT_SSH_FILE):
    if DISABLED:
        return
    required_version = split_version_string(required_version)
    version = get_version(filename)
    if version < required_version:
        raise Exception('Your version of openssh, %s, is older than the '
                        'required version, %s' % (
                            to_string(version), to_string(required_version)))
