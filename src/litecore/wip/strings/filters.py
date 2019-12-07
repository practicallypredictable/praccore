import string

from typing import (
    Dict,
    Optional,
)

TransTable = Dict[int, Optional[int]]

DEFAULT_TRANS_TABLE = str.maketrans(
    '', '', ''.join(c for c in string.punctuation if c not in ('-', '_'))
)


def only_alpha(s: str) -> str:
    return ''.join(filter, str.isalpha, s)


def only_alpha_numeric(s: str) -> str:
    return ''.join(filter(str.isalnum, s))


def strip_ws(s: str) -> str:
    return ''.join(s.split())


def ws_to_us(s: str) -> str:
    return '_'.join(s.split())


def ws_to_dash(s: str) -> str:
    return '-'.join(s.split())


def dash_to_us(s: str) -> str:
    return s.replace('-', '_')


def us_to_dash(s: str) -> str:
    return s.replace('_', '-')


def strip_punct_except_dash_us(
        s: str,
        *,
        trans_table: TransTable = DEFAULT_TRANS_TABLE,
) -> str:
    return s.translate(trans_table)
