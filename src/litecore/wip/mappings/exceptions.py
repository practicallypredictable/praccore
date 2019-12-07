from litecore import LitecoreError


class KeyTypeError(LitecoreError, TypeError):
    """Encountered a mapping key with invalid type."""
    pass


class KeyValueError(LitecoreError, ValueError):
    """Encountered a mapping key with invalid value."""
    pass


class OneToOneKeyError(LitecoreError, ValueError):
    """Encountered a key or value insert/update violating a one-to-one mapping.

    Only relevant for mapping types designed to reject such attempts.

    """
    pass
