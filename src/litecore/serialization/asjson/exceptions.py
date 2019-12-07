from litecore import LitecoreError as _ErrorBase


class JSONError(_ErrorBase):
    pass


class JSONRuntimeError(JSONError, RuntimeError):
    pass


class JSONDeserializationError(JSONError, ValueError):
    pass


class JSONSerializationError(JSONError):
    pass


class JSONSerializationTypeError(JSONSerializationError, TypeError):
    pass


class JSONSerializationValueError(JSONSerializationError, ValueError):
    pass
