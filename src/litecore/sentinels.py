"""Support the creation of singleton sentinel objects.

"""
import copyreg


class _Sentinel:
    _instances = {}

    def __new__(cls, name: str):
        instance = cls._instances.get(name)
        if instance is not None:
            return instance
        return super().__new__(cls)

    def __init__(self, name):
        self._name = name
        self._instances[name] = self

    def __bool__(self):
        return False

    def __repr__(self):
        return f'<Sentinel: {self._name}>'

    def __getnewargs__(self):
        return (self._name,)


def create(name: str) -> _Sentinel:
    """Create and return a named singleton to serve as a sentinel.

    Make sure to assign the returned object to a module-level name which is the
    same as the name supplied as the argument to the create() function.

    The returned object always tests as False in boolean operations.

    Arguments:
        name: the name of the singleton instance

    Returns:
        singleton instance

    >>> MISSING = create('MISSING')
    >>> MISSING
    <Sentinel: MISSING>
    >>> bool(MISSING)
    False
    >>> not MISSING
    True
    >>> hash(MISSING) is not None
    True
    >>> create('SAME') == create('SAME')
    True
    >>> create('SAME') == create('DIFFERENT')
    False
    >>> create('SAME') is create('SAME')
    True
    >>> type(create('SAME')) is type(create('SAME'))
    True
    >>> import copy
    >>> copy.deepcopy(MISSING) is MISSING
    True
    >>> import pickle
    >>> pickle.loads(pickle.dumps(MISSING)) is MISSING
    True

    """
    return _Sentinel(name)


def _unpickler(name: str):
    if name in _Sentinel._instances:
        return _Sentinel._instances[name]
    return create(name)


def _pickler(sentinel: _Sentinel):
    return _unpickler, sentinel.__getnewargs__()


copyreg.pickle(_Sentinel, _pickler, _unpickler)
