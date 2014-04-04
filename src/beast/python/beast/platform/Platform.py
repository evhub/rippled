from __future__ import absolute_import, division, print_function, unicode_literals

import platform

def _get_platform_string():
    system = platform.system()
    parts = [system]
    if system == 'Darwin':
        ten, major, minor = platform.mac_ver().split('.')
        parts.extend([ten, major, minor])
    elif system == 'Windows':
        raise Exception("TODO: Can't handle windows builds yet.")
    elif system == 'Linux':
        flavor, version, _ = platform.linux_distribution()
        parts.append(flavor)
        parts.extend(version.split('.'))
    else:
        raise Exception("Don't understand how to build for platform " + system)
    return '.'join(parts)

PLATFORM = _get_platform_string()

