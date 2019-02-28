"""Support the creation of unique singleton sentinel objects.

"""
__all__ = (
    'create',
    'MISSING',
)

from typing import Optional

_DEFAULT_NAME = '<Not Named>'


def create(*, name: Optional[str] = None):
    """Create and return a new instance of a new class to serve as a sentinel.

    Args:
        name (optional): the name of the sentinel instance
    Returns:
        instance of newly-created sentinel class

    By design, each call will return an instance of a distinct, newly-created
    class (even calls having the same name argument). Notice that the __init__
    method for the created class takes no arguments. Therefore, it is impossible
    to create additional instances of the same class.

    If provided, the name argument should match the module-level name to which
    the result is being assigned. This will assure the object is pickleable. The
    returned instance will have a __reduce__ method to support pickling.

    In this usage, make sure to assign the returned object to a module-level
    name (which in Python is a singleton object by definition).

    If no name argument is provided, the returned object will have a default
    internal name and no __reduce__ method. There is no need to enforce that
    the name to which the object is assigned matches the internal name, but the
    resulting object will not be pickleable.

    The returned object always tests as False in boolean operations.

    >>> MISSING = create(name='MISSING')
    >>> MISSING
    <Sentinel(MISSING)>
    >>> bool(MISSING)
    False
    >>> create()
    <Sentinel(<Not Named>)>
    >>> create(name='SAME') == create(name='SAME')
    False
    >>> type(create(name='SAME')) == type(create(name='SAME'))
    False

    """
    class Sentinel:
        def __init__(self):
            if name is None:
                self._name = _DEFAULT_NAME
                self._named = False
            else:
                self._name = name
                self._named = True

        def __repr__(self):
            return f'<{self.__class__.__name__}({self._name})>'

        if name is not None:
            # Make object pickleable; module-level name must match given name
            def __reduce__(self):
                return self._name

        def __bool__(self):
            return False

    return Sentinel()


MISSING = create(name='MISSING')
