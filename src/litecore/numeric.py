from fractions import Fraction
import numbers

from typing import (
    Tuple,
)


def as_ratio(x: numbers.Real) -> Tuple[int, int]:
    """Return integer numerator and denominator for a real number.

    The fraction defined by the returned numerator and denominator will be
    in lowest terms.

    >>> import math
    >>> as_ratio(math.pi)
    (3141592653589793, 1000000000000000)
    >>> as_ratio(0.25)
    (1, 4)
    >>> as_ratio(math.sqrt(2))
    (14142135623730951, 10000000000000000)
    >>> from decimal import Decimal
    >>> as_ratio(Decimal('3.14159'))
    (314159, 100000)
    >>> as_ratio('3.14159')
    Traceback (most recent call last):
     ...
    ValueError: Could not interpret value '3.14159'; must be numeric

    """
    try:
        n = int(x)
        s = str(x)
    except Exception as err:
        msg = f'Could not interpret value {x!r}; must be numeric'
        raise ValueError(msg) from err
    if n == x:
        return n, 1
    if 'e' in s:   # scientific notation
        sign = '-' if x < 0 else ''
        digits, exponent = s.split('e')
        digits = digits.replace('.', '').replace('-', '')
        if exponent.isdigit():
            exponent = int(exponent)
        else:
            msg = f'Invalid numeric value {x!r}; implied exponent {exponent}'
            raise ValueError(msg)
        padding = '0' * (abs(exponent)-1)
        if exponent > 0:
            s = f'{sign}{digits}{padding}.0'
        else:
            s = f'{sign}0.{padding}{digits}'
    s = s.split('.')
    n = int(''.join(s))
    d = 10 ** len(s[1])
    f = Fraction(n, d)
    return f.numerator, f.denominator
