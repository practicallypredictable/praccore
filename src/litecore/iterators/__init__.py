"""Functions and classes for processing general iterables and iterators.

These functions are intended to support a functional programming style, and
build upon the itertools standard library module.

A number of the functions are taken from or are minor improvements upon the
itertools recipes. See:
    https://docs.python.org/3/library/itertools.html#itertools-recipes

A number of the functions are also inspired by, and borrow heavily from,
a few packages on PyPI, including:
    https://pypi.org/project/toolz/
    https://pypi.org/project/more-itertools/
    https://pypi.org/project/boltons/
    https://pypi.org/project/ubelt/

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

from .cached import (  # noqa: F401
    CachedIterator,
)

from .exceptions import (  # noqa: F401
    IterableTooShortError,
    IterableTooLongError,
)

from .recipes import (  # noqa: F401
    iter_with,
    argsort,
    consume,
    only_one,
    first,
    except_first,
    nth,
    tail,
    last,
    except_last,
    unique_with_index,
    unique,
    argunique,
    take,
    take_specified,
    take_batches,
    peek,
    drop,
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

from .reductions import (  # noqa: F401
    ilen,
    iminmax,
    decreasing,
    increasing,
    non_decreasing,
    non_increasing,
    same_items,
    same_items_unhashable,
    same_ordered_items,
    all_distinct_items,
    all_equal_items_sorted,
    all_equal_items_sequence,
    inner_product,
)

from .flatten import (  # noqa: F401
    flatten,
    flatten_map,
    flatten_deep,
)

from .pluck import (  # noqa: F401
    pluck,
)

from .runlengths import (  # noqa: F401
    Run,
    RunLengths,
)
