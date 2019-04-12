import collections


class LRUOrderedDict(collections.OrderedDict):
    """Implement least-recently-used cache.

    Limit size and evict the least-recently looked-up key when full.

    From the recipe in the Python documentation:
        https://docs.python.org/3/library/collections.html#collections.OrderedDict

    """
    __slots__ = ('_maxlen')

    def __init__(self, maxlen=256, *args, **kwargs):
        self._maxlen = maxlen
        super().__init__(*args, **kwargs)

    @property
    def maxlen(self) -> int:
        return self._maxlen

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.maxlen!r}, {collections.OrderedDict(self)!r})'

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxlen:
            oldest = next(iter(self))
            del self[oldest]
