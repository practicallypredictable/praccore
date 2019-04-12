import logging

from typing import (
    Callable,
    Optional,
)

import litecore.utils

log = logging.getLogger(__name__)


class TransactionError(litecore.utils.LitecoreError, RuntimeError):
    """Attempted to use an unprepared or invalid transaction."""
    pass


class RollbackError(TransactionError):
    """Encountered an error during rollback after a previous error."""
    pass


def undoer(func: Callable, *args, **kwargs):
    def inner():
        func(*args, **kwargs)
    return inner


class TransactionManager:
    def __init__(self, *, name: Optional[str] = None, reraise: bool = True):
        self._name = str(name) if name else 'Unnamed Transaction'
        self._reraise = bool(reraise)
        self._prepared = False
        self._stack = []

    @property
    def prepared(self) -> bool:
        """Prepare a transaction to accept undo steps, rollback or commit."""
        return self._prepared

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        try:
            transaction_error = issubclass(exc_type, TransactionError)
        except TypeError:
            transaction_error = False
        if exc_type is not None and not transaction_error:
            self.rollback()
        suppress_exc = not transaction_error and not self._reraise
        return suppress_exc

    def prepare(self):
        if self._stack:
            msg = f'Undo stack has active items; check commit logic'
            raise TransactionError(msg)
        self._prepared = True

    def _validate(self) -> None:
        if not self.prepared:
            msg = f'Transaction not yet prepared'
            raise TransactionError(msg)

    def push_undo(self, undo: UndoStep):
        self._validate()
        self._stack.append(undo)

    def rollback(self):
        self._validate()
        while self._stack:
            undo = self._stack.pop()
            try:
                undo()
            except Exception as err:
                msg = f'Could not perform rollback action calling {undo!r}'
                raise RollbackError(msg) from err
        assert len(self._stack) == 0
        self._prepared = False

    def commit(self):
        self._validate()
        self._stack.clear()
        self._prepared = False
