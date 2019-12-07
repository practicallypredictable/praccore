from typing import (
    Any,
    Mapping,
    Sequence,
    Optional,
    Tuple,
)


def _arg_repr(arg_seq: Optional[Sequence] = None) -> str:
    if arg_seq is None:
        return ''
    return ', '.join(f'{v!r}' for v in arg_seq)


def _kwarg_repr(kwarg_dict: Optional[Mapping] = None) -> str:
    if kwarg_dict is None:
        return ''
    return ', '.join(f'{k}={v!r}' for k, v in sorted(kwarg_dict.items()))


def simple_repr(
        obj: Any,
        *,
        args: Optional[Tuple[str]] = None,
        kwargs: Optional[Tuple[str]] = None,
        arg_seq: Optional[Sequence[Any]] = None,
        kwarg_dict: Optional[Mapping[str, Any]] = None,
) -> str:
    """Meaningful simple repr() for custom classes.

    """
    sep = ',' if (args and kwargs) else ''
    full_name = type(obj).__qualname__
    if arg_seq is None and args is not None:
        arg_seq = [getattr(obj, arg) for arg in args]
    if kwarg_dict is None and kwargs is not None:
        kwarg_dict = {kwarg: getattr(obj, kwarg) for kwarg in kwargs}
    return f'{full_name}({_arg_repr(arg_seq)}{sep}{_kwarg_repr(kwarg_dict)})'
