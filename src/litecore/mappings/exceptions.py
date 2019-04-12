import litecore.utils


class KeyTypeError(litecore.utils.LitecoreError, TypeError):
    """Encountered a mapping key with invalid type."""
    pass


class KeyValueError(litecore.utils.LitecoreError, ValueError):
    """Encountered a mapping key with invalid value."""
    pass


class DuplicateKeyError(litecore.utils.LitecoreError, ValueError):
    """Encountered an attempt to insert/update an already-existing key.

    Only relevant for mapping types designed to reject such attempts.

    """
    pass


class OneToOneKeyError(litecore.utils.LitecoreError, ValueError):
    """Encountered a key or value insert/update violating a one-to-one mapping.

    Only relevant for mapping types designed to reject such attempts.

    """
    pass
