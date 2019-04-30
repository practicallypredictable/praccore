"""Useful functions for processing sequences, iterables and iterators.

These functions are intended to support a functional programming style, and
build upon the itertools standard library module.

A number of the functions are taken from or are minor improvements upon the
itertools recipes. See:
    https://docs.python.org/3/library/itertools.html#itertools-recipes

A number of the functions are also inspired by, and borrow heavily from,
a few third-party packages on PyPI, including:
    https://github.com/pytoolz/toolz
    https://github.com/erikrose/more-itertools
    https://github.com/kachayev/fn.py

Many of those packages were developed years ago and support legacy Python 2.
Some of these packages implement what are conceptually the same functions in
inconsistent ways. The versions included here are intended to refresh these
ideas for Python 3.6+.

There is very little exception-handling in this sub-package. Most functions
leverage off of Python built-ins or the itertools module in the standard
library. Exceptions raised by the underlying built-ins or itertools calls
will generally be propagated back to the caller undisturbed. Basic errors
such as passing non-iterable objects where an iterable is expected, or non-
integral arguments where an int is expected, will generally be detected
by the underlying built-in or itertools function.

"""
from .slice import (  # noqa: F401
    adjust_slice_endpoint,
    adjust_slice_args,
    slice_indices,
    iter_slice,
)

from .classes import (  # noqa: F401
    SequenceProxyType,
    CachedIterator,
)

from .linkedlist import (  # noqa: F401
    Node,
    SingleLinkNode,
    SinglyLinkedList,
    DoubleLinkNode,
    DoublyLinkedList,
)

from .orderedset import (  # noqa: F401
    OrderedSet,
)

from .mixins import (  # noqa: F401
    logged_sequence,
    LoggedSequenceMixin,
)

from .runlengths import (  # noqa: F401
    Run,
    RunLengths,
)

from .reductions import (  # noqa: F401
    ilen,
    decreasing,
    increasing,
    non_decreasing,
    non_increasing,
    same_items,
    same_items_unhashable,
    same_ordered_items,
    all_distinct_items,
    all_equal_items,
    all_equal_items_sequence,
    inner_product,
)

from .sequences import (  # noqa: F401
    DO_NOT_FLATTEN,
    consume,
    take,
    take_batches,
    groups_of,
    peek,
    drop,
    unique,
    first,
    only_one,
    skip_first,
    nth,
    tail,
    last,
    flatten,
    flatten_recursive,
    flatmap,
    prepend,
    pad,
    finite_cycle,
    enumerate_cycle,
    round_robin,
    round_robin_longest,
    rotate_cycle,
    intersperse,
    partition,
    split,
    take_then_split,
    split_after,
    split_before,
    window,
    pairwise,
    replace,
    tabulate,
    difference,
    iterate,
    keep_calling,
    force_reverse,
    zip_strict,
    unzip,
    unzip_finite,
    most_recent_run,
    groupby_unsorted,
)

from .find import (  # noqa: F401
    find_all,
)

from .sorting import (  # noqa: F401
    prioritize,
    prioritize_where,
)
