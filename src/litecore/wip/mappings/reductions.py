from typing import (
    Mapping,
)

import litecore.sequences


def is_one_to_one(mapping: Mapping) -> bool:
    """Returns True if a mapping has unique values.

    Python mappings have unique keys, so a mapping is one-to-one if the values
    are all distinct.

    >>> is_one_to_one({'a': 1, 'b': 2, 'c': 3})
    True
    >>> is_one_to_one({'a': 1, 'b': 2, 'c': 2})
    False

    """
    return litecore.sequences.all_distinct_items(mapping.values())
