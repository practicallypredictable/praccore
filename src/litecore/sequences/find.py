import collections
import logging

log = logging.getLogger(__name__)


def find_all(items, sequence):
    found = collections.defaultdict(list)
    for i, item in enumerate(sequence):
        if item in items:
            found[item].append(i)
    for item, indexes in found.items():
        yield item, (index for index in indexes)
