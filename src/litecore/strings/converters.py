import logging
import re

log = logging.getLogger(__name__)

_FIRST_CAPITAL_REGEX = re.compile('(.)([A-Z][a-z]+)')
