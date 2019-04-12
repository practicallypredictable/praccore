import collections
import itertools
import logging

from typing import (
    NamedTuple,
)

log = logging.getLogger(__name__)

# this is for dict of lists/tuples/etc


def make_named_from(
        mapping,
        *,
        name: str = 'Record',
):
    Record = collections.namedtuple(name, mapping.keys())
    for fields in zip(
            *(mapping.values())):
        yield Record(*fields)


def make_named_longest_from(
        mapping,
        *,
        name: str = 'Record',
        fillvalue=None,
):
    Record = collections.namedtuple(name, mapping.keys())
    for fields in itertools.zip_longest(
            *(mapping.values()), fillvalue=fillvalue):
        yield Record(*fields)


def make_ordered_named_from(
        mapping,
        *,
        field_order,
        name: str = 'Record',
):
    Record = collections.namedtuple(name, field_order)
    for fields in zip(
            *(mapping[field] for field in field_order)):
        yield Record(*fields)


def make_ordered_named_longest_from(
        mapping,
        *,
        field_order,
        name: str = 'Record',
        fillvalue=None,
):
    Record = collections.namedtuple(name, field_order)
    for fields in itertools.zip(
            *(mapping[field] for field in field_order), fillvalue=fillvalue):
        yield Record(*fields)
