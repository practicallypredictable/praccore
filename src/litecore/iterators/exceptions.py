from litecore import LitecoreError


class IterableTooShortError(LitecoreError, ValueError):
    pass


class IterableTooLongError(LitecoreError, ValueError):
    pass
