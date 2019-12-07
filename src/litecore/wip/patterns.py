import logging

log = logging.getLogger(__name__)


class Fluid:
    def __init__(self, obj):
        self._Fluid_obj = obj

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._Fluid_obj!r})'

    def __getattr__(self, name: str):
        attr = getattr(self._Fluid_obj, name)
        if callable(attr):
            def get_instance(*args, **kwargs):
                attr(*args, **kwargs)
                return self
            return get_instance
        else:
            return attr
