import re


VALID_IDENTIFIER_RE = re.compile(r"^[_A-Za-z][_0-9A-Za-z]*$")
NO_DOUBLE_US_RE = re.compile(r"^[0-9A-Za-z]+(_[0-9A-Za-z]+)*(?<!_{2})$")


def is_nonempty_string(s: str) -> bool:
    return isinstance(s, str) and s.strip() != ''


def is_valid_identifier(s: str) -> bool:
    """

    Examples:

    >>> is_valid_identifier('this_is_valid')
    True
    >>> is_valid_identifier('')
    False
    >>> is_valid_identifier('2this_is_invalid')
    False
    >>> is_valid_identifier('ThisIsValid')
    True
    >>> is_valid_identifier('_')
    True
    >>> is_valid_identifier('_this_is_valid')
    True
    >>> is_valid_identifier('so_is_this_')
    True
    >>> is_valid_identifier('_sunder_')
    True
    >>> is_valid_identifier('__dunder__')
    True
    >>> is_valid_identifier('__this_is_not__a__dunder_but_valid__')
    True
    >>> is_valid_identifier('_2leading_underscore_makes_this_valid')
    True
    >>> is_valid_identifier('2_')
    False
    >>> is_valid_identifier('__2leading_dunder_makes_this_valid')
    True
    >>> is_valid_identifier('_2_')
    True
    >>> is_valid_identifier('HTTPResponseCode')
    True

    """
    return VALID_IDENTIFIER_RE.match(s) is not None


def is_dunder(s: str) -> bool:
    """

    Examples:

    >>> is_dunder('__dunder__')
    True
    >>> is_dunder('')
    False
    >>> is_dunder('__not_')
    False
    >>> is_dunder('_not__')
    False
    >>> is_dunder('__another_dunder__')
    True
    >>> is_dunder('___not_a_dunder__')
    False
    >>> is_dunder('__also_not_a_dunder___')
    False
    >>> is_dunder('__a_tricky__case__')
    False
    >>> is_dunder('__an___even_tricker___case__')
    False
    >>> is_dunder('___')
    False
    >>> is_dunder('____')
    False
    >>> is_dunder('_____')
    False
    >>> is_dunder('__2__')
    True
    >>> is_dunder('__HTTPResponseCode__')
    True

    """
    if len(s) < 5 or s[:2] != '__' or s[-2:] != '__':
        return False
    return NO_DOUBLE_US_RE.match(s[2:-2]) is not None


def is_sunder(s: str) -> bool:
    """

    Examples:

    >>> is_sunder('_sunder_')
    True
    >>> is_sunder('__not_')
    False
    >>> is_sunder('_not__')
    False
    >>> is_sunder('_another_sunder_')
    True
    >>> is_sunder('__not_a_sunder_')
    False
    >>> is_sunder('_also_not_a_sunder__')
    False
    >>> is_sunder('_a_tricky__case_')
    False
    >>> is_sunder('_an___even_tricker___case_')
    False
    >>> is_sunder('___')
    False
    >>> is_sunder('____')
    False
    >>> is_sunder('_____')
    False
    >>> is_sunder('_2_')
    True
    >>> is_sunder('_HTTPResponseCode_')
    True

    """
    if len(s) < 3 or s[0] != '_' or s[-1] != '_':
        return False
    return NO_DOUBLE_US_RE.match(s[1:-1]) is not None
