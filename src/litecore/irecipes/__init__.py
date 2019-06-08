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

Many of the functions in this sub-package will never complete or raise an
exception if passed an infinite iterator. Take care when using infinite
iterators.

There are certain modules which are not automatically imported into the package
namespace, and which must be specifically imported for use. These are:

    containers: functions which provide some special functionality for mappings
        and sequences (which have items accessed by subscripting)

    joins: functions for in-memory joins of mappings based upon keys

    records: functions for making records with named fields out of mappings

    computations: functions which only really make sense for iterables of
        numeric types

"""
from .common import (  # noqa: F401
    peek,
    consume,
    take,
    drop,
    pairwise,
    window,
    take_batches,
    keyed_items,
    flag_where,
)

from .select import (  # noqa: F401
    only_one,
    first,
    nth,
    tail,
    last,
    except_last,
)

from .unique import (  # noqa: F401
    enumerate_unique,
    unique,
    argunique,
    unique_hashable,
)

from .rotate import (  # noqa: F401
    finite_cycle,
    enumerate_cycle,
    round_robin,
    round_robin_longest,
    rotate_cycle,
    intersperse,
)

from .modify import (  # noqa: F401
    prepend,
    pad,
    partition,
    split,
    take_then_split,
    split_after,
    split_before,
    replace,
    replace_multi,
)

from .flatten import (  # noqa: F401
    flatten,
    flatmap,
    deepflatten,
)

from .group import (  # noqa: F401
    prioritize_in,
    prioritize_where,
    groupby_unsorted,
    groupby_sorted,
    unique_just_seen,
    Run,
    RunLengths,
)

from .zipped import (  # noqa: F401
    zip_strict,
    unzip,
    unzip_finite,
    unzip_longest_finite,
)

from .reductions import (  # noqa: F401
    ilen,
    iminmax,
    count_where,
    allpairs,
    decreasing,
    increasing,
    nondecreasing,
    nonincreasing,
    allunique,
    allunique_hashable,
    allequal,
    allequal_sequence,
    allequal_sorted,
)

from .misc import (  # noqa: F401
    force_reverse,
    iter_with,
    tabulate,
    iterate,
    iter_except,
    repeatfunc,
)

from .classes import (  # noqa: F401
    IteratorBoundError,
    BoundedIterator,
    CachedIterator,
)
