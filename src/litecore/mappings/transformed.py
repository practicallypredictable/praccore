

class TransformedMapping(BaseMapping):
    __slots__ = ('_transform')

    def __init__(self, transform, iterable_or_mapping=(), **kwargs):
        super().__init__(iterable_or_mapping, **kwargs)
        self._transform = transform

    def __getitem__(self, key):
        return super().__getitem__(self._transform(key))

    def __iter__(self):
        return (orig_key for orig_key, value in super().values())

    def transformed_items(self):
        return ((key, value[1]) for key, value in super().items())

    def __eq__(self, other) -> bool:
        if not isinstance(other, collections.abc.Mapping):
            return NotImplemented
        if len(self) != len(other):
            return False
        other = type(self)(other)
        other_items = other.mapping_factory(other.transformed_items())
        return self.mapping_factory(self.transformed_items()) == other_items


class TransformedMutableMapping(TransformedMapping, BaseMutableMapping):
    __slots__ = ()

    def __setitem__(self, key, value):
        super().__setitem__(self._transform(key), (key, value))

    def __delitem__(self, key):
        super().__delitem__(self._transform(key))


# TODO: checking pickling/json/copy/deepcopy for all concrete (__slots__!)
# TODO: dict vs factory in pickling/copy?
# TODO: performance optimiozatinos for all abc methods
# TODO: need optimized __eq__? hashable?
