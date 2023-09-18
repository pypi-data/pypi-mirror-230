from __future__ import annotations

import re
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Union,
)

FMT_STR_MAP: Dict[str, str] = {
    "-": "minus",
    "+": "plus",
    "!": "exclamation",
    "*": "asterisk",
}

FMT_STR_OTAN_MAP: Dict[str, str] = {
    "A": "alpha",
    "B": "bravo",
    "C": "charlie",
    "D": "delta",
    "E": "echo",
    "F": "foxtrot",
    "G": "golf",
    "H": "hotel",
    "I": "india",
    "J": "juliet",
    "K": "kilo",
    "L": "lima",
    "M": "mike",
    "N": "november",
    "O": "oscar",
    "P": "papa",
    "Q": "quebec",
    "R": "romeo",
    "S": "sierra",
    "T": "tango",
    "U": "uniform",
    "V": "victor",
    "W": "whiskey",
    "X": "xray",
    "Y": "yankee",
    "Z": "zulu",
}

concat: Callable[[Union[List[str], Iterable[str]]], str] = "".join


def itself(x: Any = None) -> Any:
    """Return itself value"""
    return x


def caller(func: Union[Callable[[], Any], Any]) -> Any:
    """Call function if it was callable

    .. usage::
        >>> some_func = lambda: 100
        >>> caller(some_func)
        100
    """
    return func() if callable(func) else func


def convert_fmt_str(fmt: str) -> str:
    """Convert format string to format string name

    .. usage::
        >>> convert_fmt_str('%a')
        'alpha'
        >>> convert_fmt_str('%!b')
        'bravo_exclamation'
        >>> convert_fmt_str('%S')
        'sierra_upper'
        >>> convert_fmt_str('%-N')
        'november_upper_minus'
        >>> convert_fmt_str('G')
        'G'
        >>> convert_fmt_str('%H')
        'hotel_upper'
    """
    _fmt_re: str = fmt
    if search := re.search(r"^%(?P<prefix>[-+!*]?)(?P<format>[a-zA-Z])$", fmt):
        search_dict = search.groupdict()
        _fmt: str
        if (_fmt := search_dict["format"]).isupper():
            _fmt_re = f"{FMT_STR_OTAN_MAP[_fmt]}upper"
        else:
            _fmt = _fmt.upper()
            _fmt_re = FMT_STR_OTAN_MAP[_fmt]

        if prefix := search_dict["prefix"]:
            _fmt_re = f"{_fmt_re}{FMT_STR_MAP[prefix]}"
    return _fmt_re
