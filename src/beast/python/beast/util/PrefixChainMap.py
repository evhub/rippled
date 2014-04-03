from __future__ import absolute_import, division, print_function, unicode_literals

from beast.compatibility.ChainMap import ChainMap

def _get_items_with_prefix(key, mapping):
    """Get all elements from the mapping whose keys are a prefix of the given
    key, sorted by decreasing key length."""
    for k, v in reversed(sorted(mapping.items())):
        if key.startswith(k):
            yield v

def prefix_chain_map(key, mapping):
    return ChainMap(*_get_items_with_prefix(key, mapping))
