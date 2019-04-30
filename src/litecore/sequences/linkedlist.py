import collections
import reprlib

from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import litecore.sequences.slice

NodeType = TypeVar('NodeType', bound='Node')


class Node(Generic[NodeType]):
    __slots__ = ()


class SingleLinkNode(Node):
    __slots__ = ('value', 'next')

    def __init__(
            self,
            value: Any,
            *,
            next_node: Optional[Node] = None,
    ):
        self.value = value
        self.next = next_node

    def __repr__(self):
        return f'{type(self).__name__}({self.value!r})'

    def __getnewargs_ex__(self):
        return ((self.value,), {'next_node': self.next})


class DoubleLinkNode(SingleLinkNode):
    __slots__ = ('prev',)

    def __init__(
            self,
            *args,
            prev_node: Optional[Node] = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.prev = prev_node

    def __getnewargs_ex__(self):
        args, kwargs = super().__getnewargs_ex__()
        kwargs.update({'prev_node': self.prev})
        return (args, kwargs)


class _LinkedList(collections.abc.MutableSequence):
    __slots__ = ('_len', '_head', '_tail')

    def __init__(self, iterable: Optional[Iterable[Any]] = None):
        self._len = 0
        self._head = None
        self._tail = None
        if iterable is not None:
            self.extend(iterable)

    @reprlib.recursive_repr()
    def __repr__(self):
        return f'{type(self).__name__}([' + ', '.join(map(repr, self)) + '])'

    def __len__(self):
        return self._len

    def __iter__(self):
        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def __eq__(self, other):
        if not isinstance(other, collections.abc.Sequence):
            return False
        elif len(self) != len(other):
            return False
        else:
            return list(self) == list(other)

    def __hash__(self):
        msg = f'unhashable type: {type(self).__name__}'
        raise TypeError(msg)

    def __getstate__(self):
        return (tuple(self),)

    def __setstate__(self, state):
        self.__init__(state[0])

    def __copy__(self):
        return type(self)(self)

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = type(self)()
        memo[id(self)] = new
        new.__init__(deepcopy(item) for item in self)
        return new

    def _adjust_index(self, index: int) -> int:
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError('list index out of range')
        return index

    def _find_value(
            self,
            value,
            *,
            start: Optional[int] = None,
            stop: Optional[int] = None,
            find_all: bool = False,
    ) -> Tuple[Node, List[int]]:
        skip, stop, _ = litecore.sequences.slice.adjust_slice_args(
            length=self._len,
            start=start,
            stop=stop,
        )
        index = 0
        found = []
        node = self._head
        while index < stop and node is not None:
            if not skip and node.value == value:
                found.append(index)
                if not find_all:
                    break
            index += 1
            if skip > 0:
                skip -= 1
            node = node.next
        if len(found) == 0:
            msg = f'{value!r} is not in list'
            raise ValueError(msg)
        else:
            return (node, found)

    def copy(self):
        return self.__copy__()

    def extendleft(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.appendleft(item)

    def extend(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.append(item)

    def index(self, value: Any, start=None, stop=None) -> None:
        node, found = self._find_value(value, start=start, stop=stop)
        return found[0]

    def count(self, value: Any) -> int:
        try:
            node, found = self._find_value(value, find_all=True)
        except ValueError:
            return 0
        else:
            return len(found)

    def sort(
            self,
            *,
            key: Optional[Callable] = None,
            reverse: bool = False,
    ) -> None:
        items = sorted(self, key=key, reverse=reverse)
        self.clear()
        self.extend(items)


class SinglyLinkedList(_LinkedList):
    def __reversed__(self):
        items = sorted(list(self), reverse=True)
        return iter(items)

    def __getitem__(self, index_or_slice: Union[int, slice]):
        if isinstance(index_or_slice, slice):
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node, _ = self._advance_to(start)
            results = []
            while node is not None:
                results.append(node.value)
                node, _ = self._advance(node, step)
            return results
        else:
            node, _ = self._advance_to(index_or_slice)
            return node.value

    def __setitem__(
            self,
            index_or_slice: Union[int, slice],
            value: Union[Any, Iterable[Any]],
    ):
        if isinstance(index_or_slice, slice):
            indices = [
                i for i in litecore.sequences.slice.slice_indices(
                    length=self._len,
                    start=index_or_slice.start,
                    stop=index_or_slice.stop,
                    step=index_or_slice.step,
                ) if i < self._len
            ]
            try:
                values = list(value)
                if len(values) != len(indices):
                    msg = (
                        f'attempt to assign sequence of size {len(values)} '
                        f'to extended slice of size {len(indices)}'
                    )
                    raise ValueError(msg)
            except TypeError:
                raise TypeError('must assign iterable to extended slices')
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node, _ = self._advance_to(start)
            for value in values:
                node.value = value
                node, _ = self._advance(node, step)
        else:
            node, _ = self._advance_to(index_or_slice)
            node.value = value

    def _del_node(self, node: Node, prev: Node) -> None:
        if node is self._head:
            self._head = node.next
        else:
            prev.next = node.next
        self._len -= 1

    def __delitem__(self, index_or_slice: Union[int, slice]):
        if isinstance(index_or_slice, slice):
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node, prev = self._advance_to(start)
            while node is not None:
                next_node, prev = self._advance(node, step)
                self._del_node(node, prev)
                node = next_node
        else:
            node, prev = self._advance_to(index_or_slice)
            self._del_node(node, prev)

    def _advance_to(self, index: int) -> Tuple[Node, Node]:
        index = self._adjust_index(index)
        steps = index
        node = self._head
        prev = None
        while steps > 0 and node is not None:
            prev = node
            node = node.next
            steps -= 1
        return node, prev

    def _advance(self, node: Node, step: int) -> Tuple[Node, Node]:
        assert step >= 0
        steps = step
        prev = None
        while steps > 0 and node is not None:
            prev = node
            node = node.next
            steps -= 1
        return node, prev

    def clear(self) -> None:
        node = self._head
        while node is not None:
            next_node = node.next
            node.next = None
            node = next_node
        self._head = self._tail = None
        self._len = 0

    def appendleft(self, value: Any) -> None:
        self._head = SingleLinkNode(value, next_node=self._head)
        if self._tail is None:
            self._tail = self._head
        self._len += 1

    def append(self, value: Any) -> None:
        node = SingleLinkNode(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._len += 1

    def extendleft(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.appendleft(item)

    def extend(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.append(item)

    def popleft(self):
        if self._head is None:
            assert self._tail is None
            raise IndexError('pop from an empty list')
        value = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._len -= 1
        return value

    def pop(self):
        if self._tail is None:
            assert self._head is None
            raise IndexError('pop from an empty list')
        value = self._tail.value
        if self._head is self._tail:
            assert self._head.next is None
            self._head = self._tail = None
            self._len = 0
            return value
        node = self._head
        prev = None
        while node is not None:
            prev = node
            node = node.next
            if node is self._tail:
                break
        assert node is self._tail
        prev.next = None
        self._tail = prev
        self._len -= 1
        return value

    def index(self, value: Any, start=None, stop=None) -> None:
        node, found = self._find_value(value, start=start, stop=stop)
        return found[0]

    def count(self, value: Any) -> int:
        try:
            node, found = self._find_value(value, find_all=True)
        except ValueError:
            return 0
        else:
            return len(found)

    def remove(self, value: Any) -> None:
        node = self._head
        prev = None
        while node is not None and node.value != value:
            prev = node
            node = node.next
        if prev is None:
            self._head = node.next
        elif node is not None:
            prev.next = node.next
            node.next = None
        self._len -= 1

    def insert(self, index: int, value: Any) -> None:
        if self._head is None:
            assert self._tail is None
            self.append(value)
            return
        target, prev = self._advance_to(index)
        node = SingleLinkNode(
            value,
            next_node=target,
        )
        if prev is not None:
            prev.next = node
        if target is self._head:
            self._head = node
        self._len += 1

    def insert_after(self, index: int, value: Any) -> None:
        if self._head is None:
            assert self._tail is None
            self.append(value)
            return
        target, _ = self._advance_to(index)
        node = SingleLinkNode(
            value,
            next_node=target.next,
        )
        if target is not None:
            target.next = node
        if target is self._tail:
            self._tail = node
        self._len += 1

    def reverse(self) -> None:
        if self._tail is self._head:
            return
        node = self._head
        prev_node = None
        next_node = None
        while node is not None:
            next_node = node.next
            node.next = prev_node
            prev_node = node
            node = next_node
        self._tail = self._head
        self._head = prev_node


class DoublyLinkedList(_LinkedList):
    def __reversed__(self):
        node = self._tail
        while node is not None:
            yield node.value
            node = node.prev

    def __getitem__(self, index_or_slice: Union[int, slice]):
        if isinstance(index_or_slice, slice):
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node = self._seek(start)
            results = []
            while node is not None:
                results.append(node.value)
                node = self._move_relative(node, step)
            return results
        else:
            node = self._seek(index_or_slice)
            return node.value

    def __setitem__(
            self,
            index_or_slice: Union[int, slice],
            value: Union[Any, Iterable[Any]],
    ):
        if isinstance(index_or_slice, slice):
            indices = [
                i for i in litecore.sequences.slice.slice_indices(
                    length=self._len,
                    start=index_or_slice.start,
                    stop=index_or_slice.stop,
                    step=index_or_slice.step,
                ) if i < self._len
            ]
            try:
                values = list(value)
                if len(values) != len(indices):
                    msg = (
                        f'attempt to assign sequence of size {len(values)} '
                        f'to extended slice of size {len(indices)}'
                    )
                    raise ValueError(msg)
            except TypeError:
                raise TypeError('must assign iterable to extended slices')
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node = self._seek(start)
            for value in values:
                node.value = value
                node = self._move_relative(node, step)
        else:
            node = self._seek(index_or_slice)
            node.value = value

    def _del_node(self, node: Node) -> None:
        if node is self._head:
            self._head = node.next
            node.next.prev = None
        elif node is self._tail:
            self._tail = node.prev
            node.prev.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        self._len -= 1

    def __delitem__(self, index_or_slice: Union[int, slice]):
        if isinstance(index_or_slice, slice):
            start = index_or_slice.start
            if start is None:
                start = 0
            step = index_or_slice.step
            if step is None:
                step = 1
            node = self._seek(start)
            while node is not None:
                next_node = self._move_relative(node, step)
                self._del_node(node)
                node = next_node
        else:
            node = self._seek(index_or_slice)
            self._del_node(node)

    def _adjust_index(self, index: int) -> int:
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError('list index out of range')
        return index

    def _find_value(
            self,
            value,
            *,
            start: Optional[int] = None,
            stop: Optional[int] = None,
            find_all: bool = False,
    ) -> Tuple[Node, List[int]]:
        skip, stop, _ = litecore.sequences.slice.adjust_slice_args(
            length=self._len,
            start=start,
            stop=stop,
        )
        index = 0
        found = []
        node = self._head
        while index < stop and node is not None:
            if not skip and node.value == value:
                found.append(index)
                if not find_all:
                    break
            index += 1
            if skip > 0:
                skip -= 1
            node = node.next
        if len(found) == 0:
            msg = f'{value!r} is not in list'
            raise ValueError(msg)
        else:
            return (node, found)

    def _seek(self, index: int) -> Node:
        index = self._adjust_index(index)
        if index > self._len // 2:
            steps = self._len - index - 1
            node = self._tail
            while steps > 0 and node is not None:
                node = node.prev
                steps -= 1
        else:
            steps = index
            node = self._head
            while steps > 0 and node is not None:
                node = node.next
                steps -= 1
        return node

    def _move_relative(self, node: Node, step: int) -> Node:
        steps = abs(step)
        while steps > 0 and node is not None:
            if step > 0:
                node = node.next
            else:
                node = node.prev
            steps -= 1
        return node

    def clear(self) -> None:
        node = self._head
        while node is not None:
            next_node = node.next
            self._del_node(node)
            node = next_node

    def appendleft(self, value: Any) -> None:
        node = DoubleLinkNode(value, next_node=self._head)
        if self._head is None:
            self._head = self._tail = node
        else:
            self._head.prev = node
            self._head = node
        self._len += 1

    def append(self, value: Any) -> None:
        node = DoubleLinkNode(value)
        if self._tail is None:
            assert self._head is None
            self._head = self._tail = node
        else:
            node.prev = self._tail
            self._tail.next = node
            self._tail = node
        self._len += 1

    def popleft(self):
        if self._head is None:
            assert self._tail is None
            raise IndexError('pop from an empty list')
        value = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        else:
            self._head.prev = None
        self._len -= 1
        return value

    def pop(self):
        if self._tail is None:
            assert self._head is None
            raise IndexError('pop from an empty list')
        value = self._tail.value
        self._tail = self._tail.prev
        if self._tail is None:
            self._head = None
        else:
            self._tail.next = None
        self._len -= 1
        return value

    def remove(self, value: Any) -> None:
        node, found = self._find_value(value)
        if node is not None:
            if node.prev is not None:
                node.prev.next = node.next
                node.next.prev = node.prev
            else:
                self._head = node.next
                node.next.prev = None
        self._len -= 1

    def insert(self, index: int, value: Any) -> None:
        if self._head is None:
            assert self._tail is None
            self.append(value)
            return
        target = self._seek(index)
        node = DoubleLinkNode(
            value,
            prev_node=target.prev,
            next_node=target,
        )
        if target.prev is not None:
            target.prev.next = node
        target.prev = node
        if target is self._head:
            self._head = node
        self._len += 1

    def insert_after(self, index: int, value: Any) -> None:
        if self._head is None:
            assert self._tail is None
            self.append(value)
            return
        target = self._seek(index)
        node = DoubleLinkNode(
            value,
            prev_node=target,
            next_node=target.next,
        )
        if target.next is not None:
            target.next.prev = node
        target.next = node
        if target is self._tail:
            self._tail = node
        self._len += 1

    def rotate(self, n: int = 1) -> None:
        if not n:
            return
        if self._len > 0:
            n %= self._len
            if n > 0:
                app = self.appendleft
                pop = self.pop
            else:
                app = self.append
                pop = self.popleft
            for _ in range(n):
                app(pop())
