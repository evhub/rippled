from __future__ import absolute_import, division, print_function, unicode_literals

import platform

def _get_platform_string():
    system = platform.system()
    parts = [system]
    if system == 'Linux':
        flavor, version, _ = platform.linux_distribution()
        parts.append(flavor)
        parts.extend(version.split('.'))
    elif system == 'Darwin':
        ten, major, minor = platform.mac_ver()[0].split('.')
        parts.extend([ten, major, minor])
    elif system == 'Windows':
        release, version, csd, ptype = platform.win32_ver()
        parts.extend([release, version, csd, ptype])
    elif system == 'FreeBSD':
        # No other variables to pass with FreeBSD that Python provides and I could find
        pass
    else:
        raise Exception("Don't understand how to build for platform " + system)
    return '.'.join(parts)

PLATFORM = _get_platform_string()
