import re

import litecore.utils
import litecore.strings.check as _check
import litecore.strings.filters as _filters


IS_CAMEL_CASE_RE = re.compile(
    r"(?:[a-z][0-9a-z]*)(?:[A-Z][0-9a-z]*)+"
)

IS_SNAKE_CASE_RE = re.compile(
    r"^$"
)

_CAMEL_CASE_REGEX = re.compile(r'([A-Z])')
_SNAKE_CASE_REGEX = re.compile(r'([a-z])([A-Z])')
_TITLE_CASE_REGEX = re.compile(r"[A-za-z]+('[A-za-z]+)?")


def is_camel_case(s: str) -> bool:
    """

    Examples:

    >>> is_camel_case('isCamelCase')
    True
    >>> is_camel_case('not_camel_case')
    False
    >>> is_camel_case('NotCamelCase')
    False
    >>> is_camel_case('notcamelcase')
    False
    >>> is_camel_case('NOTCAMELCASE')
    False
    >>> is_camel_case('Notcamelcase')
    False
    >>> is_camel_case('not_Camel_Case')
    False
    >>> is_camel_case('notCamelCase_')
    False
    >>> is_camel_case('isCamel2Case')
    True

    """
    return IS_CAMEL_CASE_RE.match(s) is not None


def first_lower(s: str) -> str:
    if not s:
        return s
    if len(s) > 1:
        return s[0].lower() + s[1:]
    else:
        return s[0].lower()


def first_upper(s: str) -> str:
    if not s:
        return s
    if len(s) > 1:
        return s[0].upper() + s[1:]
    else:
        return s[0].upper()


def _prepare_string(s: str) -> str:
    s = strip_punctuation(s)
    return litecore.strings.filters.whitespace_to_dash(s).replace('-', '_')


def _common_camel(s: str, *, join_char: str = '') -> str:
    s = _prepare_string(s)
    split = re.sub(_CAMEL_CASE_REGEX, r'_\1', s).split('_')
    if len(split) > 1:
        s = join_char.join(component.title() for component in split)
    return s


def _strip_inner_dunders(s: str) -> str:
    pass


def camel_case(s: str) -> str:
    """Return a string in camelCase format.

    Examples:

    >>> camel_case('thisShouldBeUnchanged')
    'thisShouldBeUnchanged'
    >>> camel_case('this_should_change')
    'thisShouldChange'
    >>> camel_case('This-should-Change')
    'thisShouldChange'
    >>> camel_case('ThisShouldChange')
    'thisShouldChange'
    >>> camel_case('')
    ''
    >>> camel_case('A')
    'a'
    >>> camel_case('This-Is-Weird')
    'thisIsWeird'
    >>> camel_case('This_isWeirder!!')
    'thisIsWeirder'
    >>> camel_case('-This_isTruly#?:!  #.,/ --  bizarre(*) does this work?')
    'thisIsTrulyBizarreDoesThisWork'

    """
    if not s:
        return s
    elif len(s) == 1:
        return s.lower()
    return first_lower(_common_camel(s))


def snake_case(s: str) -> str:
    """Return a string in snake_case format.

    Examples:

    >>> snake_case('this_should_be_unchanged')
    'this_should_be_unchanged'
    >>> snake_case('thisShouldChange')
    'this_should_change'
    >>> snake_case('This-should-Change')
    'this_should_change'
    >>> snake_case('ThisShouldChange')
    'this_should_change'
    >>> snake_case('')
    ''
    >>> snake_case('A')
    'a'
    >>> snake_case('This-Is-Weird')
    'this_is_weird'
    >>> snake_case('This_isWeirder')
    'this_is_weirder'
    >>> snake_case('-This_isTruly#?:!  #.,! --  bizarre(*) does this work?')
    '_this_is_truly____bizarre_does_this_work'
    >>> snake_case('how about this---?')
    'how_about_this___'

    """
    if not s:
        return s
    elif len(s) == 1:
        return s.lower()
    s = first_lower(_prepare_string(s))
    return re.sub(_SNAKE_CASE_REGEX, r'\1_\2', s).lower()


def pascal_case(s: str) -> str:
    """Return a string in PascalCase format.

    Examples:

    >>> pascal_case('ThisShouldBeUnchanged')
    'ThisShouldBeUnchanged'
    >>> pascal_case('this_should_change')
    'ThisShouldChange'
    >>> pascal_case('this-should-Change')
    'ThisShouldChange'
    >>> pascal_case('thisShouldChange')
    'ThisShouldChange'
    >>> pascal_case('')
    ''
    >>> pascal_case('A')
    'A'
    >>> pascal_case('This-Is-Weird')
    'ThisIsWeird'
    >>> pascal_case('This_isWeirder!!')
    'ThisIsWeirder'
    >>> pascal_case('-This_isTruly#?:!  #.,/ --  bizarre(*) does this work?')
    'ThisIsTrulyBizarreDoesThisWork'

    """
    if not s:
        return s
    elif len(s) == 1:
        return s.upper()
    return first_upper(_common_camel(s))


def lisp_case(s: str) -> str:
    """Return a string in lisp-case format.

    Examples:

    >>> lisp_case('this-should-be-unchanged')
    'this-should-be-unchanged'
    >>> lisp_case('thisShouldChange')
    'this-should-change'
    >>> lisp_case('This-should-Change')
    'this-should-change'
    >>> lisp_case('ThisShouldChange')
    'this-should-change'
    >>> lisp_case('')
    ''
    >>> lisp_case('A')
    'a'
    >>> lisp_case('This-Is-Weird')
    'this-is-weird'
    >>> lisp_case('This_isWeirder')
    'this-is-weirder'
    >>> lisp_case('-This_isTruly#?:!  #.,! --  bizarre(*) does this work?')
    '-this-is-truly----bizarre-does-this-work'
    >>> lisp_case('how about this---?')
    'how-about-this---'

    """
    if not s:
        return s
    elif len(s) == 1:
        return s.lower()
    return snake_case(s).replace('_', '-')


def darwin_case(s: str) -> str:
    """Return a string in PascalCase format.

    Examples:

    >>> darwin_case('This_Should_Be_Unchanged')
    'This_Should_Be_Unchanged'
    >>> darwin_case('this_should_change')
    'This_Should_Change'
    >>> darwin_case('this-should-Change')
    'This_Should_Change'
    >>> darwin_case('thisShouldChange')
    'This_Should_Change'
    >>> darwin_case('')
    ''
    >>> darwin_case('A')
    'A'
    >>> darwin_case('This-Is-Weird')
    'This_Is_Weird'
    >>> darwin_case('This_isWeirder!!')
    'This_Is_Weirder'
    >>> darwin_case('-This_isTruly#?:!  #.,/ --  bizarre(*) does this work?')
    'This_Is_Truly_Bizarre_Does_This_Work'

    """
    if not s:
        return s
    elif len(s) == 1:
        return s.upper()
    return first_upper(_common_camel(s, join_char='_')).lstrip('_')


def title_case(s: str) -> str:
    """Improved title case to handle apostrophes in contractions.

    Examples:

    >>> title_case("they're bill's friends.")
    "They're Bill's Friends."

    """
    return re.sub(_TITLE_CASE_REGEX, lambda m: first_upper(m.group(0)), s)
