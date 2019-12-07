import dataclasses
import dis
import inspect
import itertools

from typing import (
    Any,
    Callable,
    List,
)


def all_slots(class_obj: Any) -> List[str]:
    slots = itertools.chain.from_iterable(
        getattr(cls, '__slots__', ()) for cls in inspect.getmro(class_obj))
    return sorted(set(slots))


def slotted_fields(
        _cls=None,
        *,
        with_dict: bool = False,
        with_weakref: bool = False,
):
    def decorator(cls):
        if '__slots__' in cls.__dict__:
            msg = f'{cls.__name__} already has __slots__'
            raise TypeError(msg)
        cls_dict = dict(cls.__dict__)
        field_names = list(f.name for f in dataclasses.fields(cls))
        if with_dict:
            # TODO: check if any mro class has dict???
            # https://github.com/cjrh/autoslot/blob/master/autoslot.py
            field_names.append('__dict__')
        if with_weakref:
            field_names.append('__weakref__')
        cls_dict['__slots__'] = tuple(field_names)
        for name in field_names:
            cls_dict.pop(name, None)
        cls_dict.pop('__dict__', None)
        cls_dict.pop('__weakref__', None)
        cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
        qualname = getattr(cls, '__qualname__', None)
        if qualname is not None:
            cls.__qualname__ = qualname
        return cls

    return decorator if _cls is None else decorator(_cls)


def assigned_attributes(method: Callable) -> List[str]:
    bytecode = dis.Bytecode(method)
    it1, it2 = itertools.tee(bytecode)
    next(it2, None)
    self_var = next(iter(method.__code__.co_varnames))
    attrs = set()
    for first, second in zip(it1, it2):
        if (first.argval == self_var and (
                first.opname, second.opname == ('LOAD_FAST', 'STORE_ATTR'))):
            attrs.add(second.argval)
    return sorted(attrs)
