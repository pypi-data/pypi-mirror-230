# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
# mypy: disable-error-code="attr-defined"
"""
The main object of formatter is able to format every thing you want by less
config when inherit base class.
"""
from __future__ import annotations

import inspect
import math
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache, partial, total_ordering
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    final,  # docs: https://github.com/python/mypy/issues/9953
)

# TODO: Review ``semver`` package instead ``packaging``.
#  docs: https://pypi.org/project/semver/
import packaging.version as pck_version
from dateutil.relativedelta import relativedelta
from ddeutil.core import can_int, remove_pad  # type: ignore

from .exceptions import (
    FormatterArgumentError,
    FormatterGroupArgumentError,
    FormatterGroupValueError,
    FormatterKeyError,
    FormatterValueError,
)
from .utils import (
    caller,
    concat,
    convert_fmt_str,
    itself,
)

FormatterType = Type["Formatter"]
FormatterGroupType = Type["__FormatterGroup"]
ConstantType = Type["__BaseConstant"]

PriorityCallable = Union[Callable[[Any], Any], Callable[[], Any], partial]
FormatterCallable = Union[Callable[[], Any], partial]


class PriorityValue(TypedDict):
    """Type Dictionary for value of mapping of ``cls.priorities``"""

    value: PriorityCallable
    level: Optional[Union[int, Tuple[int, ...]]]


@final
class CRegexValue(TypedDict):
    """Type Dictionary for value of mapping of ``cls.formatter``"""

    value: Union[FormatterCallable, str]
    cregex: str


@final
class RegexValue(TypedDict):
    """Type Dictionary for value of mapping of ``cls.formatter``"""

    value: Union[FormatterCallable, str]
    regex: str


ReturnPrioritiesType = Dict[str, PriorityValue]
ReturnFormattersType = Dict[str, Union[CRegexValue, RegexValue]]


@total_ordering
class SlotLevel:
    """Slot level object for order priority values. This was mean if
    you implement this slot level object to attribute on your class
    and update level to an instance when it has some action, it will
    be make the level more than another instance.

    :param level: a level number of the slot object.
    :type level: int

    .. attributes:

        - count
        - value

    .. methods:

        - update

    """

    __slots__ = (
        "level",
        "slot",
    )

    def __init__(self, level: int) -> None:
        """Main initialize of the slot object that define a slot list
        with level input value length of False.
        """
        self.level: int = level
        self.slot: List[bool] = [False] * level

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(level={self.level})>"

    def __str__(self) -> str:
        return str(self.level)

    def __hash__(self) -> int:
        return hash(tuple(self.slot))

    def __eq__(self, other: Union[SlotLevel, Any]) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __lt__(self, other: SlotLevel) -> bool:
        return self.value < other.value

    @property
    def count(self) -> int:
        """Return the counting number of True value in the slot.

        :rtype: int
        :return: the counting number of True value in the slot.
        """
        return len(list(filter(lambda x: x is True, self.slot)))

    @property
    def value(self) -> int:
        """Return a sum of weighted value from a True value in any slot
        position.

        :rtype: int
        :return: a sum of weighted value from a True value in any slot
            position.
        """
        return sum(x[0] * int(x[1]) for x in enumerate(self.slot, start=1))

    def update(
        self,
        numbers: Optional[Union[int, Tuple[int, ...]]] = None,
        strict: bool = True,
    ) -> SlotLevel:
        """Update value in slot from False to True

        :param numbers: updated numbers of this SlotLevel object.
        :type numbers: Union[int, tuple]
        :param strict: a strict flag for raise error when pass out of
            range numbers.
        :type strict: bool(=True)

        :raises ValueError: if updated number does not exist in range.

        :rtype: SlotLevel
        :return: Self that was updated level
        """
        _numbers: Union[int, Tuple[int, ...]] = numbers or (0,)
        for num in SlotLevel.make_tuple(_numbers):
            if num == 0:
                continue
            elif 0 <= (_num := (num - 1)) <= (self.level - 1):
                self.slot[_num] = True
                continue
            if strict:
                raise FormatterValueError(
                    f"number for update the slot level object does not "
                    f"in range of 0 and {self.level}."
                )
        return self

    @staticmethod
    def make_tuple(value: Union[int, Tuple[int, ...]]) -> Tuple[int, ...]:
        """Return tuple of integer value that was created from input value
        parameter if it is not tuple.

        :param value: a tuple of integers or any integer
        :type value: Union[int, tuple]

        :rtype: tuple
        """
        return (value,) if isinstance(value, int) else value


@dataclass(frozen=True)
class PriorityData:
    """Priority Data class

    .. dataclass attributes::

        - value: PriorityCallable
        - level: Optional[Union[int, Tuple[int, ...]]]
    """

    value: PriorityCallable = field(default=itself, repr=False)
    level: Optional[Union[int, Tuple[int, ...]]] = field(default=(0,))


class MetaFormatter(metaclass=ABCMeta):
    """Metaclass Formatter object that implement `__slots__` attribute for any
    instance classes.

    .. meta-class attributes::

        - __slots__: Tuple[str, ...]
    """

    __slots__: Tuple[str, ...] = ()


@total_ordering
class Formatter(MetaFormatter):
    """Formatter object for inherit to any formatter subclass that define
    format and parse method. The base class will implement necessary
    properties and method for subclass that should implement or enhance such
    as `the cls.formatter()` method or the `cls.priorities` property.

    :param formats: A mapping value of priority attribute data.
    :type formats: Optional[dict](=None)

    .. class attributes::

        - base_fmt: str
        - base_level: int : the maximum level of slot level of this instance
        - Config: object : Configuration object

    .. attributes::

        - value
        - string
        - validate
        - level
        - priorities
        - __priorities

    .. methods::

        - formatter
        - default

    .. seealso::

        This class is abstract class for any formatter class. It will raise
    `NotImplementedError` when the necessary attributes and methods does not
    implement from subclass.
    """

    # This value must reassign from child class
    base_fmt: str = ""

    # This value must reassign from child class
    base_level: int = 1

    class Config:
        """Base Configuration for any subclass of formatter"""

        base_config_value: Optional[Any] = None

    def __init_subclass__(
        cls: FormatterType,
        /,
        level: int = 1,
        **kwargs: Any,
    ) -> None:
        cls.base_level = level
        super().__init_subclass__(**kwargs)

        if not cls.base_fmt:
            raise NotImplementedError(
                "Please implement base_fmt class property for this "
                "sub-formatter class."
            )
        if not cls.__slots__:
            raise NotImplementedError(
                "Please implement `__slots__` class property for this "
                "sub-formatter class."
            )

    @classmethod
    def passer(
        cls,
        value: Any,
    ) -> Formatter:
        """Passer the value of this formatter subclass data.

        :param value: an any value that able to pass to `cls.formatter` method.
        :type value: Any
        """
        fmt_filter = [
            (k, caller(v["value"]))
            for k, v in cls.formatter(value).items()
            if k in re.findall("(%[-+!*]?[A-Za-z])", cls.base_fmt)
        ]
        fmts, values = zip(*fmt_filter)
        return cls.parse(value="_".join(values), fmt="_".join(fmts))

    @classmethod
    def parse(
        cls,
        value: str,
        fmt: Optional[str] = None,
    ) -> Formatter:
        """Parse string value with its format to subclass of formatter object.
        This method generates the value for itself data that can be formatted
        to another format string values.

        :param value: a string value that match with fmt.
        :type value: str
        :param fmt: a format value will use `cls.base_fmt` if it does not pass
            from input argument.
        :type fmt: Optional[str](=None)

        :raises NotImplementedError: if fmt value parameter does not pass form
            input, or `cls.base_fmt` does not implement.
        :raises ValueError: if value does not match with regular expression
            format string.

        :rtype: Formatter
        :return: an instance of Formatter that parse from string value by
            format string.
        """
        _fmt: str = fmt or cls.base_fmt

        if not _fmt:
            raise NotImplementedError(
                "This Formatter class does not set default format string "
                "value."
            )

        _fmt = cls.gen_format(_fmt)
        if _search := re.search(rf"^{_fmt}$", value):
            return cls(_search.groupdict())

        raise FormatterValueError(
            f"value {value!r} does not match with format {_fmt!r}"
        )

    @classmethod
    def gen_format(
        cls,
        fmt: str,
        *,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        alias: bool = True,
    ) -> str:
        """Generate format string value that combine from any matching of
        format name with format regular expression value that able to search.

        :param fmt: a format string value pass from input argument.
        :type fmt: str
        :param prefix
        :type prefix: Optional[str]
        :param suffix
        :type suffix: Optional[str]
        :param alias
        :type alias: bool
        """
        _cache: Dict[str, int] = defaultdict(lambda: 0)
        _prefix: str = prefix or ""
        _suffix: str = suffix or ""
        for fmt_match in re.finditer(r"(%[-+!*]?[A-Za-z])", fmt):
            fmt_str: str = fmt_match.group()
            regex: str = cls.regex()[fmt_str]
            if _alias_match := re.search(
                r"^\(\?P<(?P<alias_name>\w+)>(?P<fmt_regex>.+)?\)$",
                regex,
            ):
                _sr_re: str = _alias_match.group("alias_name")
                if alias:
                    regex = re.sub(
                        rf"\(\?P<{_sr_re}>",
                        f"(?P<{_prefix}{_sr_re}__{_cache[fmt_str]}{_suffix}>",
                        regex,
                    )
                else:
                    regex = re.sub(rf"\(\?P<{_sr_re}>", "(", regex)
            else:
                raise FormatterValueError(
                    "Regex format string does not set group name for parsing "
                    "value to its class."
                )
            _cache[fmt_str] += 1
            fmt = fmt.replace(fmt_str, regex, 1)
        return fmt

    @classmethod
    @lru_cache(maxsize=None)
    def regex(cls) -> Dict[str, str]:
        """Return mapping of formats and regular expression values of
        `cls.formatter`.

        :rtype: Dict[str, str]
        :return: a mapping of format, and it's regular expression string
            like:
                {
                    "%n": "(?P<normal>...)",
                    ...
                }
        """
        results: Dict[str, str] = {}
        pre_results: Dict[str, str] = {}
        for f, props in cls.formatter().items():
            if "regex" in props:
                results[f] = props["regex"]
            elif "cregex" in props:
                pre_results[f] = props["cregex"]
            else:
                raise FormatterValueError(
                    "formatter does not contain `regex` or `cregex` "
                    "in dict value"
                )
        for f, cr in pre_results.items():
            cr = cr.replace("%%", "[ESCAPE]")
            for cm in re.finditer(r"(%[-+!*]?[A-Za-z])", cr):
                cs: str = cm.group()
                if cs in results:
                    cr = cr.replace(cs, results[cs], 1)
                else:
                    raise FormatterArgumentError(
                        "format",
                        (
                            f"format cregex string that contain {cs} regex "
                            f"does not found."
                        ),
                    )
            results[f] = cr.replace("[ESCAPE]", "%%")
        return results

    def values(self, value: Optional[Any] = None) -> Dict[str, str]:
        """Return mapping of formats and formatter values of `cls.formatter`

        :rtype: Dict[str, str]
        :return: a mapping of formats and formatter values like:
                {
                    "%n": "normal-value",
                    ...
                }
        """
        return {
            f: caller(props["value"])
            for f, props in self.formatter(value or self.value).items()
        }

    def format(self, fmt: str) -> str:
        """Return string value that was filled by the input format pattern
        argument.

        :param fmt: a format string value for mapping with formatter.
        :type fmt: str

        :raises KeyError: if it has any format pattern does not found in
            `cls.formatter`.

        :rtype: str
        :return: a formatted string value
        """
        _fmts: ReturnFormattersType = self.formatter(self.value)
        fmt = fmt.replace("%%", "[ESCAPE]")
        for _fmt_match in re.finditer(r"(%[-+!*]?[A-Za-z])", fmt):
            _fmt_str: str = _fmt_match.group()
            try:
                _value: Union[FormatterCallable, str] = _fmts[_fmt_str]["value"]
                fmt = fmt.replace(_fmt_str, caller(_value))
            except KeyError as err:
                raise FormatterKeyError(
                    f"the format: {_fmt_str!r} does not support for "
                    f"{self.__class__.__name__!r}"
                ) from err
        return fmt.replace("[ESCAPE]", "%")

    def __init__(
        self,
        formats: Optional[Dict[str, Any]] = None,
        *,
        set_std_value: bool = True,
    ) -> None:
        """Main initialization get the format mapping from input argument
        and generate the necessary attributes for define the value of this
        base formatter object.

            The setter of attribute does not do anything to __slot__ variable.
        """
        _formats: Dict[str, Any] = self.__validate_format(formats or {})

        # Set level of SlotLevel object that set from `base_level` and pass this
        # value to _level variable for update process in priorities loop.
        self._level = SlotLevel(level=self.base_level)
        _level: SlotLevel = self._level

        # Set None default of any set up value in `cls.__slots__`
        for attr in getattr(self, "__slots__", ()):
            if attr != (self.__class__.__name__.lower()):
                setattr(self, attr, None)

        for name, props in self.__priorities.items():
            # Split name of key of priorities property value.
            # From: <prefix>_<body> -> TO: [<prefix>, <body>]
            attr = name.split("_", maxsplit=1)[0]

            # Set attr condition
            if getattr(self, attr):
                continue
            elif any(name.endswith(i) for i in {"_default", "_fix"}):
                setattr(self, attr, caller(props.value))

                # Update level by default it will update at first level
                _level.update(props.level)
            elif name in _formats:
                setattr(
                    self,
                    attr,
                    props.value(_formats[name]),  # type: ignore[call-arg]
                )

                # Update level by default it will update at first level
                _level.update(props.level)

        # Run validate method.
        if not self.validate:
            raise FormatterValueError(
                "Parsing value does not valid from validator"
            )

        # Set standard property by default is string value or `self.string`
        if set_std_value:
            setattr(
                self,
                self.__class__.__name__.lower(),
                str(self.string),
            )

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __hash__(self) -> int:
        """Return hashed string value of str property"""
        return hash(self.string)

    def __str__(self) -> str:
        """Return string value of str property"""
        return self.string

    def __repr__(self) -> str:
        """Return represent string"""
        return (
            f"<{self.__class__.__name__}"
            f".parse('{self.string}', "
            f"'{self.base_fmt}')>"
        )

    def __eq__(self, other: Union[Formatter, Any]) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __lt__(self, other: Formatter) -> bool:
        return self.value.__lt__(other.value)  # type: ignore[no-any-return]

    @property
    @abstractmethod
    def value(self) -> Any:  # pragma: no cover
        """Return the value object that define by any subclass."""
        raise NotImplementedError(
            "Please implement value property for this sub-formatter class"
        )

    @property
    @abstractmethod
    def string(self) -> str:  # pragma: no cover
        """Return standard string value that define by any subclass."""
        raise NotImplementedError(
            "Please implement string property for this sub-formatter class"
        )

    @property
    def validate(self) -> bool:
        """Validate method that will run after setup all attributes"""
        return True

    def valid(self, value: str, fmt: str) -> bool:
        """Return true if the value attribute from parser of string and
        fmt is valid with self.value.

        :param value:
        :param fmt:
        """
        return self.value.__eq__(  # type: ignore[no-any-return]
            self.__class__.parse(value, fmt).value,
        )

    @property
    def level(self) -> SlotLevel:
        """Return the slot level object of any subclass."""
        return self._level

    @property
    def __priorities(self) -> Dict[str, PriorityData]:
        """Return private property of extracted mapping from
        `self.priorities` value.
        """
        return {k: PriorityData(**v) for k, v in self.priorities.items()}

    @staticmethod
    def __validate_format(formats: Dict[str, Any]) -> Dict[str, Any]:
        """Raise error if any duplication format name do not all equal."""
        results: Dict[str, Any] = {}
        for fmt in formats:
            _fmt: str = fmt.split("__", maxsplit=1)[0]
            if _fmt not in results:
                results[_fmt] = formats[fmt]
                continue
            if results[_fmt] != formats[fmt]:
                raise FormatterValueError(
                    "Parsing with some duplicate format name that have "
                    "value do not all equal."
                )
        return results

    @property
    @abstractmethod
    def priorities(
        self,
    ) -> ReturnPrioritiesType:
        """Return priorities"""
        raise NotImplementedError(
            "Please implement priorities property for this sub-formatter class"
        )

    @staticmethod
    @abstractmethod
    def formatter(
        value: Optional[Any] = None,
    ) -> ReturnFormattersType:
        """Return formatter"""
        raise NotImplementedError(
            "Please implement formatter static method for this "
            "sub-formatter class"
        )

    @staticmethod
    def default(value: str) -> Callable[[], str]:
        """Return wrapper function of value"""
        return lambda: value

    def to_const(self) -> ConstantType:
        """Convert this Sub-formatter instance to Constant."""
        return dict2const(
            self.values(),
            name=f"{self.__class__.__name__}Const",
            base_fmt=self.base_fmt,
        )

    @staticmethod
    @abstractmethod
    def prepare_value(value: Any) -> Any:
        raise NotImplementedError(
            "Please implement prepare_value static method for this "
            "sub-formatter class."
        )

    def __add__(self, other: Any) -> Formatter:
        if not isinstance(other, self.__class__):
            try:
                return self.__class__.passer(value=self.value + other)
            except FormatterValueError:
                return NotImplemented
        return self.__class__.passer(value=self.value + other.value)

    def __radd__(self, other: Any) -> Formatter:
        return self.__add__(other)

    def __sub__(self, other: Any) -> Formatter:
        try:
            if not isinstance(other, self.__class__):
                return self.__class__.passer(value=(self.value - other))
            return self.__class__.passer(value=(self.value - other.value))
        except FormatterValueError:
            return NotImplemented

    def __rsub__(self, other: Any) -> Any:
        try:
            return other - self.value
        except (TypeError, FormatterValueError):
            return NotImplemented


class Serial(Formatter):
    """Serial object for register process that implement formatter and
    parser.
    """

    base_fmt: str = "%n"

    class Config(Formatter.Config):
        """Configuration of Serial object"""

        serial_max_padding: int = 3
        serial_max_binary: int = 8

    __slots__ = (
        "number",
        "serial",
    )

    @property
    def value(self) -> int:
        return int(self.string)

    @property
    def string(self) -> str:
        return self.number  # type: ignore[no-any-return]

    @property
    def priorities(
        self,
    ) -> ReturnPrioritiesType:
        return {
            "number": {
                "value": lambda x: x,
                "level": 1,
            },
            "number_pad": {
                "value": lambda x: remove_pad(x),
                "level": 1,
            },
            "number_binary": {
                "value": lambda x: str(int(x, 2)),
                "level": 1,
            },
            "number_default": {"value": self.default("0"), "level": 0},
        }

    @staticmethod
    def formatter(
        serial: Optional[int] = None,
    ) -> ReturnFormattersType:
        """Generate formatter that support mapping formatter,
            %n  : Normal format
            %p  : Padding number
            %b  : Binary number

        :param serial: the serial value that pars to generate all format
        :type serial: Optional[int](=None)

        :rtype: Dict[str, Dict[str, Union[Callable, str]]]
        :return: the generated mapping values of all format strings
        """
        _value: int = Serial.prepare_value(serial)
        return {
            "%n": {
                "value": lambda: str(_value),
                "regex": r"(?P<number>[0-9]*)",
            },
            "%p": {
                "value": partial(Serial.to_padding, str(_value)),
                "regex": (
                    r"(?P<number_pad>"
                    rf"[0-9]{{{str(Serial.Config.serial_max_padding)}}})"
                ),
            },
            "%b": {
                "value": partial(Serial.to_binary, str(_value)),
                "regex": r"(?P<number_binary>[0-1]*)",
            },
        }

    @staticmethod
    def prepare_value(value: Optional[int]) -> int:
        if value is None:
            return 0
        if not can_int(value) or (int(value) < 0):
            raise FormatterValueError(
                f"Serial formatter does not support for value, {value!r}."
            )
        return int(value)

    @staticmethod
    def to_padding(value: str) -> str:
        """Return padding string result with zero value"""
        return (
            value.rjust(Serial.Config.serial_max_padding, "0") if value else ""
        )

    @staticmethod
    def to_binary(value: str) -> str:
        """Return binary number with limit of max zero padding"""
        return (
            f"{int(value):0{str(Serial.Config.serial_max_binary)}b}"
            if value
            else ""
        )


MONTHS: Dict[str, str] = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}

WEEKS: Dict[str, str] = {
    "Mon": "0",
    "Thu": "1",
    "Wed": "2",
    "Tue": "3",
    "Fri": "4",
    "Sat": "5",
    "Sun": "6",
}


class Datetime(Formatter, level=8):
    """Datetime object for register process that implement formatter and
    parser.
    """

    base_fmt: str = "%Y-%m-%d %H:%M:%S.%f"

    __slots__ = (
        "year",
        "month",
        "week",
        "weeks",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
        "local",
        "datetime",
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}"
            f".parse('{self.string}000', "
            f"'{self.base_fmt}')>"
        )

    @property
    def value(self) -> datetime:
        return datetime.fromisoformat(self.string)

    @property
    def string(self) -> str:
        return (
            f"{self.year}-{self.month}-{self.day} "
            f"{self.hour}:{self.minute}:{self.second}."
            f"{self.microsecond[:3]}"
        )

    @property
    def iso_date(self) -> str:
        return f"{self.year}-{self.month}-{self.day}"

    @property
    def validate(self) -> bool:  # no cov
        return True

    @property
    def priorities(
        self,
    ) -> ReturnPrioritiesType:
        """Priority Properties of the datetime object

        :rtype: Dict[str, Dict[str, Union[Callable, Tuple[int, ...], int]]]
        :returns: a priority properties of the datetime object
        """
        # TODO: Check about week value should keep first and validate if
        #  date value does not match with common sense.
        return {
            "local": {
                "value": lambda x: x,
                "level": 4,
            },
            "year": {
                "value": lambda x: x,
                "level": 8,
            },
            "year_cut_pad": {
                "value": lambda x: f"19{x}",
                "level": 8,
            },
            "year_cut": {
                "value": lambda x: f"19{x}",
                "level": 8,
            },
            "year_default": {
                "value": self.default("1990"),
                "level": 0,
            },
            "day_year": {
                "value": self._from_day_year,
                "level": (
                    7,
                    6,
                ),
            },
            "day_year_pad": {
                "value": self._from_day_year,
                "level": (
                    7,
                    6,
                ),
            },
            "month": {
                "value": lambda x: x.rjust(2, "0"),
                "level": 7,
            },
            "month_pad": {
                "value": lambda x: x,
                "level": 7,
            },
            "month_short": {
                "value": lambda x: MONTHS[x],
                "level": 7,
            },
            "month_full": {
                "value": lambda x: MONTHS[x[:3]],
                "level": 7,
            },
            "month_default": {
                "value": self.default("01"),
                "level": 0,
            },
            "day": {
                "value": lambda x: x.rjust(2, "0"),
                "level": 6,
            },
            "day_pad": {
                "value": lambda x: x,
                "level": 6,
            },
            # TODO: switch make default day before validate week
            "day_default": {
                "value": self.default("01"),
                "level": 0,
            },
            "week": {
                "value": lambda x: x,
                "level": 0,
            },
            "week_mon": {
                "value": lambda x: str(int(x) % 7),
                "level": 0,
            },
            "week_short": {
                "value": lambda x: WEEKS[x],
                "level": 0,
            },
            "week_full": {
                "value": lambda x: WEEKS[x[:3]],
                "level": 0,
            },
            "weeks_year_mon_pad": {
                "value": self._from_week_year_mon,
                "level": (
                    7,
                    6,
                ),
            },
            "weeks_year_sun_pad": {
                "value": self._from_week_year_sun,
                "level": (
                    7,
                    6,
                ),
            },
            "week_default": {
                "value": lambda: datetime.strptime(
                    self.iso_date, "%Y-%m-%d"
                ).strftime("%w"),
                "level": 0,
            },
            "hour": {
                "value": lambda x: x.rjust(2, "0"),
                "level": (
                    5,
                    4,
                ),
            },
            "hour_pad": {
                "value": lambda x: x,
                "level": (
                    5,
                    4,
                ),
            },
            "hour_12": {
                "value": (
                    lambda x: str(int(x) + 12).rjust(2, "0")
                    if self.local == "PM"
                    else x.rjust(2, "0")
                ),
                "level": 5,
            },
            "hour_12_pad": {
                "value": (
                    lambda x: str(int(x) + 12).rjust(2, "0")
                    if self.local == "PM"
                    else x
                ),
                "level": 5,
            },
            "hour_default": {
                "value": self.default("00"),
                "level": 0,
            },
            "minute": {
                "value": lambda x: x.rjust(2, "0"),
                "level": 3,
            },
            "minute_pad": {
                "value": lambda x: x,
                "level": 3,
            },
            "minute_default": {
                "value": self.default("00"),
                "level": 0,
            },
            "second": {
                "value": lambda x: x.rjust(2, "0"),
                "level": 2,
            },
            "second_pad": {
                "value": lambda x: x,
                "level": 2,
            },
            "second_default": {
                "value": self.default("00"),
                "level": 0,
            },
            "microsecond_pad": {
                "value": lambda x: x,
                "level": 1,
            },
            "microsecond_default": {
                "value": self.default("000000"),
                "level": 0,
            },
        }

    @staticmethod
    def formatter(
        dt: Optional[datetime] = None,
    ) -> ReturnFormattersType:
        """Generate formatter that support mapping formatter,
            %n  : Normal format with `%Y%m%d_%H%M%S`
            %Y  : Year with century as a decimal number.
            %y  : Year without century as a zero-padded decimal number.
            %-y : Year without century as a decimal number.
            %m  : Month as a zero-padded decimal number.
            %-m : Month as a decimal number.
            %b  : Abbreviated month name.
            %B  : Full month name.
            %a  : the abbreviated weekday name
            %A  : the full weekday name
            %w  : weekday as a decimal number, 0 as Sunday and 6 as Saturday.
            %u  : weekday as a decimal number, 1 as Monday and 7 as Sunday.
            %d  : Day of the month as a zero-padded decimal.
            %-d : Day of the month as a decimal number.
            %H  : Hour (24-hour clock) as a zero-padded decimal number.
            %-H : Hour (24-hour clock) as a decimal number.
            %I  : Hour (12-hour clock) as a zero-padded decimal number.
            %-I : Hour (12-hour clock) as a decimal number.
            %M  : minute as a zero-padded decimal number
            %-M : minute as a decimal number
            %S  : second as a zero-padded decimal number
            %-S : second as a decimal number
            %j  : day of the year as a zero-padded decimal number
            %-j : day of the year as a decimal number
            %U  : Week number of the year (Sunday as the first day of the
                week). All days in a new year preceding the first Sunday are
                considered to be in week 0.
            %W  : Week number of the year (Monday as the first day of the week
                ). All days in a new year preceding the first Monday are
                considered
                to be in week 0.
            %p  : Locale’s AM or PM.
            %f  : Microsecond as a decimal number, zero-padded on the left.

        :param dt: a datetime value
        :type dt: Optional[datetime](=None)
        """
        _dt: datetime = Datetime.prepare_value(dt)
        return {
            "%n": {
                "value": partial(_dt.strftime, "%Y%m%d_%H%M%S"),
                "cregex": "%Y%m%d_%H%M%S",
            },
            "%Y": {
                "value": partial(_dt.strftime, "%Y"),
                "regex": r"(?P<year>\d{4})",
            },
            "%y": {
                "value": partial(_dt.strftime, "%y"),
                "regex": r"(?P<year_cut_pad>\d{2})",
            },
            "%-y": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%y"),
                "regex": r"(?P<year_cut>\d{1,2})",
            },
            "%m": {
                "value": partial(_dt.strftime, "%m"),
                "regex": r"(?P<month_pad>01|02|03|04|05|06|07|08|09|10|11|12)",
            },
            "%-m": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%m"),
                "regex": r"(?P<month>1|2|3|4|5|6|7|8|9|10|11|12)",
            },
            "%b": {
                "value": partial(_dt.strftime, "%b"),
                "regex": (
                    r"(?P<month_short>"
                    r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                ),
            },
            "%B": {
                "value": partial(_dt.strftime, "%B"),
                "regex": (
                    r"(?P<month_full>"
                    r"January|February|March|April|May|June|July|"
                    r"August|September|October|November|December)"
                ),
            },
            "%a": {
                "value": partial(_dt.strftime, "%a"),
                "regex": r"(?P<week_shortname>Mon|Thu|Wed|Tue|Fri|Sat|Sun)",
            },
            "%A": {
                "value": partial(_dt.strftime, "%A"),
                "regex": (
                    r"(?P<week_fullname>"
                    r"Monday|Thursday|Wednesday|Tuesday|Friday|"
                    r"Saturday|Sunday)"
                ),
            },
            "%w": {
                "value": partial(_dt.strftime, "%w"),
                "regex": r"(?P<week>[0-6])",
            },
            "%u": {
                "value": partial(_dt.strftime, "%u"),
                "regex": r"(?P<week_mon>[1-7])",
            },
            "%d": {
                "value": partial(_dt.strftime, "%d"),
                "regex": r"(?P<day_pad>[0-3][0-9])",
            },
            "%-d": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%d"),
                "regex": r"(?P<day>\d{1,2})",
            },
            "%H": {
                "value": partial(_dt.strftime, "%H"),
                "regex": r"(?P<hour_pad>[0-2][0-9])",
            },
            "%-H": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%H"),
                "regex": r"(?P<hour>\d{2})",
            },
            "%I": {
                "value": partial(_dt.strftime, "%I"),
                "regex": (
                    r"(?P<hour_12_pad>"
                    r"00|01|02|03|04|05|06|07|08|09|10|11|12)"
                ),
            },
            "%-I": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%I"),
                "regex": r"(?P<hour_12>0|1|2|3|4|5|6|7|8|9|10|11|12)",
            },
            "%M": {
                "value": partial(_dt.strftime, "%M"),
                "regex": r"(?P<minute_pad>[0-6][0-9])",
            },
            "%-M": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%M"),
                "regex": r"(?P<minute>\d{1,2})",
            },
            "%S": {
                "value": partial(_dt.strftime, "%S"),
                "regex": r"(?P<second_pad>[0-6][0-9])",
            },
            "%-S": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%S"),
                "regex": r"(?P<second>\d{1,2})",
            },
            "%j": {
                "value": partial(_dt.strftime, "%j"),
                "regex": r"(?P<day_year_pad>[0-3][0-9][0-9])",
            },
            "%-j": {
                "value": partial(Datetime.remove_pad_dt, _dt, "%j"),
                "regex": r"(?P<day_year>\d{1,3})",
            },
            "%U": {
                "value": partial(_dt.strftime, "%U"),
                "regex": r"(?P<weeks_year_sun_pad>[0-5][0-9])",
            },
            "%W": {
                "value": partial(_dt.strftime, "%W"),
                "regex": r"(?P<weeks_year_mon_pad>[0-5][0-9])",
            },
            "%p": {
                "value": partial(_dt.strftime, "%p"),
                "regex": r"(?P<local>PM|AM)",
            },
            "%f": {
                "value": partial(_dt.strftime, "%f"),
                "regex": r"(?P<microsecond_pad>\d{6})",
            },
        }

    @staticmethod
    def prepare_value(value: Optional[datetime]) -> datetime:
        if value is None:
            return datetime.now()
        if not isinstance(value, datetime):
            raise FormatterValueError(
                f"Datetime formatter does not support for value, {value!r}."
            )
        return value

    def _from_day_year(self, value: str) -> str:
        """Return date of year"""
        _this_year: datetime = datetime.strptime(self.year, "%Y") + timedelta(
            days=int(value)
        )
        self.month = _this_year.strftime("%m")
        return _this_year.strftime("%d")

    def _from_week_year_mon(self, value: str) -> str:
        """Return validate week year with Monday value"""
        _this_week: str = (
            str(((int(self.week) - 1) % 7) + 1) if self.week else "1"
        )
        _this_year: datetime = datetime.strptime(
            f"{self.year}-W{value}-{_this_week}", "%G-W%V-%u"
        )
        self.month = _this_year.strftime("%m")
        self.day = _this_year.strftime("%d")
        return _this_year.strftime("%w")

    def _from_week_year_sun(self, value: str) -> str:
        """Return validate week year with Sunday value"""
        _this_year: datetime = datetime.strptime(
            f"{self.year}-W{value}-{self.week or '0'}", "%Y-W%U-%w"
        )
        self.month = _this_year.strftime("%m")
        self.day = _this_year.strftime("%d")
        return _this_year.strftime("%w")

    @staticmethod
    def remove_pad_dt(_dt: datetime, fmt: str) -> str:
        """Return padded datetime string that was formatted"""
        return str(remove_pad(_dt.strftime(fmt)))

    def __add__(self, other: Any) -> Formatter:
        if isinstance(other, (relativedelta, timedelta)):
            return self.__class__.passer(self.value + other)
        return NotImplemented

    def __sub__(  # type: ignore[override]
        self,
        other: Any,
    ) -> Union[Formatter, timedelta]:
        if isinstance(other, (relativedelta, timedelta)):
            return self.__class__.passer(self.value - other)
        elif isinstance(other, self.__class__):
            return self.value - other.value
        return NotImplemented

    def __rsub__(self, other: Any) -> Any:
        return NotImplemented


class Version(Formatter, level=3):
    """Version object for register process that implement formatter and
    parser.

        Version segments reference from Hatch:
        - release	        1.0.0
        - major	            2.0.0
        - minor	            1.1.0
        - micro/patch/fix   1.0.1
        - a/alpha           1.0.0a0
        - b/beta            1.0.0b0
        - c/rc/pre/preview	1.0.0rc0
        - r/rev/post	    1.0.0.post0
        - dev	            1.0.0.dev0

        Version segments reference from Semantic Versioning
        - release           1.2.3
        - pre-release       1.2.3-pre.2
        - build             1.2.3+build.4
                            1.2.3-pre.2+build.4

    .. ref::
        - The standard of versioning will align with the PEP0440
        (https://peps.python.org/pep-0440/)

        - Enhance the version object from the packaging library
        (https://packaging.pypa.io/en/latest/version.html)
    """

    base_fmt: str = "%m_%n_%c"

    __slots__ = (
        "version",
        "epoch",
        "major",
        "minor",
        "micro",
        "pre",
        "post",
        "dev",
        "local",
    )

    def __repr__(self) -> str:
        _fmt: str = "v%m.%n.%c"
        if self.epoch != "0":
            _fmt = f"%e{_fmt[1:]}"
        if self.pre:
            _fmt = f"{_fmt}%q"
        if self.post:
            _fmt = f"{_fmt}%p"
        if self.dev:
            _fmt = f"{_fmt}%d"
        if self.local:
            _fmt = f"{_fmt}%l"
        return f"<{self.__class__.__name__}.parse('{self.string}', '{_fmt}')>"

    @property
    def value(self) -> pck_version.Version:
        """"""
        return pck_version.parse(self.string)

    @property
    def string(self) -> str:
        _release: str = f"v{self.major}.{self.minor}.{self.micro}"
        if self.epoch != "0":
            _release = f"{self.epoch}!{_release[1:]}"
        if self.pre:
            _release = f"{_release}{self.pre}"
        if self.post:
            _release = f"{_release}{self.post}"
        if self.dev:
            _release = f"{_release}.{self.dev}"
        if self.local:
            _release = f"{_release}+{self.local}"
        return _release

    @property
    def priorities(
        self,
    ) -> ReturnPrioritiesType:
        return {
            "epoch": {
                "value": lambda x: x.rstrip("!"),
                "level": 3,
            },
            "epoch_num": {
                "value": lambda x: x,
                "level": 3,
            },
            "epoch_default": {
                "value": self.default("0"),
                "level": 0,
            },
            "major": {
                "value": lambda x: x,
                "level": 3,
            },
            "major_default": {
                "value": self.default("0"),
                "level": 0,
            },
            "minor": {
                "value": lambda x: x,
                "level": 2,
            },
            "minor_default": {
                "value": self.default("0"),
                "level": 0,
            },
            "micro": {
                "value": lambda x: x,
                "level": 1,
            },
            "micro_default": {
                "value": self.default("0"),
                "level": 0,
            },
            "pre": {
                "value": lambda x: self.__from_prefix(x),
                "level": 0,
            },
            "post": {
                "value": lambda x: self.__from_prefix(x),
                "level": 0,
            },
            "post_num": {
                "value": lambda x: x,
                "level": 0,
            },
            "dev": {
                "value": lambda x: x,
                "level": 0,
            },
            "local": {
                "value": lambda x: x.lstrip("+"),
                "level": 0,
            },
            "local_str": {
                "value": lambda x: x,
                "level": 0,
            },
        }

    @staticmethod
    def formatter(
        version: Optional[pck_version.Version] = None,
    ) -> ReturnFormattersType:
        """Generate formatter that support mapping formatter,
            %f  : full version format with `%m_%n_%c`
            %-f : full version format with `%m-%n-%c`
            %m  : major number
            %n  : minor number
            %c  : micro number
            %e  : epoch release
            %q  : pre-release
            %p  : post release
            %-p : post release number
            %d  : dev release
            %l  : local release
            %-l : local release number

        :param version: a version value
        :type version: Optional[packaging.version.Version](=None)

        :rtype: Dict[str, Dict[str, Union[Callable, str]]]
        :return: the generated mapping values of all format strings
        """
        _version: pck_version.Version = Version.prepare_value(version)
        return {
            "%f": {
                "value": lambda: (
                    f"{_version.major}_{_version.minor}_{_version.micro}"
                ),
                "cregex": "%m_%n_%c",
            },
            "%-f": {
                "value": lambda: (
                    f"{_version.major}_{_version.minor}_{_version.micro}"
                ),
                "cregex": "%m-%n-%c",
            },
            "%m": {
                "value": partial(str, _version.major),
                "regex": r"(?P<major>\d{1,3})",
            },
            "%n": {
                "value": partial(str, _version.minor),
                "regex": r"(?P<minor>\d{1,3})",
            },
            "%c": {
                "value": partial(str, _version.micro),
                "regex": r"(?P<micro>\d{1,3})",
            },
            "%e": {
                "value": lambda: f"{_version.epoch}!",
                "regex": r"(?P<epoch>[0-9]+!)",
            },
            "%-e": {
                "value": lambda: str(_version.epoch),
                "regex": r"(?P<epoch_num>[0-9]+)",
            },
            "%q": {
                "value": lambda: (
                    concat(map(str, _pre)) if (_pre := _version.pre) else ""
                ),
                "regex": (
                    r"(?P<pre>(a|b|c|rc|alpha|beta|pre|preview)[-_\.]?[0-9]+)"
                ),
            },
            "%p": {
                "value": lambda: str(_version.post or ""),
                "regex": (
                    r"(?P<post>(?:(post|rev|r)[-_\.]?[0-9]+)|(?:-[0-9]+))"
                ),
            },
            "%-p": {
                "value": lambda: str(_version.post or ""),
                "regex": r"(?P<post_num>[0-9]+)",
            },
            "%d": {
                "value": lambda: str(_version.dev or ""),
                "regex": r"(?P<dev>dev[-_\.]?[0-9]+)",
            },
            "%l": {
                "value": lambda: _version.local,
                "regex": r"(?P<local>\+[a-z0-9]+(?:[-_\.][a-z0-9]+)*)",
            },
            "%-l": {
                "value": lambda: f"+{_version.local}",
                "regex": r"(?P<local_str>[a-z0-9]+(?:[-_\.][a-z0-9]+)*)",
            },
        }

    @staticmethod
    def prepare_value(
        value: Optional[pck_version.Version],
    ) -> pck_version.Version:
        if value is None:
            return pck_version.parse("0.0.1")
        if not isinstance(value, pck_version.Version):
            raise FormatterValueError(
                f"Version formatter does not support for value, {value!r}."
            )
        return value

    @staticmethod
    def __from_prefix(value: str) -> str:
        """Return replaced value to standard prefix of pre- and post-format

        :param value: a pre- or post-format value
        :type value: str
        """
        for rep, matches in (
            ("a", ["alpha"]),
            ("b", ["beta"]),
            ("rc", ["c", "pre", "preview"]),
            ("post", ["rev", "r", "-"]),
        ):
            for letter in matches:
                if re.match(rf"{letter}[-_.]?[0-9]+", value):
                    return value.replace(letter, rep)
                elif re.match(rf"{rep}[-_.]?[0-9]+", value):
                    return value
        raise FormatterValueError(
            f"Convert prefix dose not valid for value `{value}`"
        )

    def __add__(self, other):  # type: ignore # no cov
        return NotImplemented

    def __sub__(self, other):  # type: ignore # no cov
        return NotImplemented

    def __rsub__(self, other):  # type: ignore # no cov
        return NotImplemented


# TODO: implement validate value of vowel and flat from values.
class Naming(Formatter, level=5):
    """Naming object for register process that implement formatter and parser.

    note: A name value that parsing to this class should not contain any
    special characters, this will keep only.
    """

    base_fmt: str = "%n"

    __slots__ = (
        "naming",
        "strings",
        "flats",
        "shorts",
        "vowels",
    )

    @property
    def value(self) -> List[str]:
        return self.string.split()

    @property
    def string(self) -> str:
        if self.strings:
            return " ".join(self.strings)
        elif self.flats:
            return self.flats[0]  # type: ignore[no-any-return]
        elif self.shorts:
            return " ".join(self.shorts)
        elif self.vowels:
            return self.vowels[0]  # type: ignore[no-any-return]
        return ""

    @property
    def priorities(
        self,
    ) -> ReturnPrioritiesType:
        return {
            "strings": {"value": lambda x: x.split(), "level": 5},
            "strings_upper": {
                "value": lambda x: x.lower().split(),
                "level": 5,
            },
            "strings_title": {
                "value": lambda x: x.lower().split(),
                "level": 5,
            },
            "strings_lower": {"value": lambda x: x.split(), "level": 5},
            "strings_camel": {
                "value": lambda x: self.__split_pascal_case(x),
                "level": 5,
            },
            "strings_pascal": {
                "value": lambda x: self.__split_pascal_case(x),
                "level": 5,
            },
            "strings_kebab": {
                "value": lambda x: x.split("-"),
                "level": 5,
            },
            "strings_kebab_upper": {
                "value": lambda x: x.lower().split("-"),
                "level": 5,
            },
            "strings_kebab_title": {
                "value": lambda x: x.lower().split("-"),
                "level": 5,
            },
            "strings_snake": {
                "value": lambda x: x.split("_"),
                "level": 5,
            },
            "strings_snake_upper": {
                "value": lambda x: x.lower().split("_"),
                "level": 5,
            },
            "strings_snake_title": {
                "value": lambda x: x.lower().split("_"),
                "level": 5,
            },
            "flats": {
                "value": lambda x: [x],
                "level": 1,
            },
            "flats_upper": {
                "value": lambda x: [x.lower()],
                "level": 1,
            },
            "shorts": {
                "value": lambda x: list(x),
                "level": 1,
            },
            "shorts_upper": {
                "value": lambda x: list(x.lower()),
                "level": 1,
            },
            "vowels": {
                "value": lambda x: [x],
                "level": 1,
            },
            "vowels_upper": {
                "value": lambda x: [x.lower()],
                "level": 1,
            },
        }

    @staticmethod
    def formatter(
        nm: Optional[Union[str, List[str]]] = None,
    ) -> ReturnFormattersType:
        """Generate formatter that support mapping formatter,

            %n  : Normal name format
            %N  : Normal name upper case format
            %-N : Normal name title case format
            %u  : Upper case format
            %l  : Lower case format
            %t  : Title case format
            %a  : Shortname format
            %A  : Shortname upper case format
            %f  : Flat case format
            %F  : Flat upper case format
            %c  : Camel case format
            %-c : Upper first Camel case format
            %p  : Pascal case format
            %s  : Snake case format
            %S  : Snake upper case format
            %-S  : Snake title case format
            %k  : Kebab case format
            %K  : Kebab upper case format
            %-K  : Kebab title case format
            %v  : normal name removed vowel
            %V  : normal name removed vowel with upper case

        :param nm:

        docs: https://gist.github.com/SuppieRK/a6fb471cf600271230c8c7e532bdae4b
        """
        _value: List[str] = Naming.prepare_value(nm)
        return {
            "%n": {
                "value": partial(Naming.__join_with, " ", _value),
                "cregex": "%l",
            },
            "%N": {
                "value": partial(
                    Naming.__join_with, " ", _value, lambda x: x.upper()
                ),
                "cregex": "%u",
            },
            "%-N": {
                "value": partial(
                    Naming.__join_with, " ", _value, lambda x: x.capitalize()
                ),
                "cregex": "%t",
            },
            "%u": {
                "value": partial(
                    Naming.__join_with, " ", _value, lambda x: x.upper()
                ),
                "regex": r"(?P<strings_upper>[A-Z0-9]+(?:\s[A-Z0-9]+)*)",
            },
            "%l": {
                "value": partial(Naming.__join_with, " ", _value),
                "regex": r"(?P<strings>[a-z0-9]+(?:\s[a-z0-9]+)*)",
            },
            "%t": {
                "value": partial(
                    Naming.__join_with, " ", _value, lambda x: x.capitalize()
                ),
                "regex": (
                    r"(?P<strings_title>[A-Z][a-z0-9]+(?:\s[A-Z]+[a-z0-9]*)*)"
                ),
            },
            "%a": {
                "value": partial(
                    Naming.__join_with,
                    "",
                    _value,
                    lambda x: (x[0] if x else ""),
                ),
                "regex": r"(?P<shorts>[a-z0-9]+)",
            },
            "%A": {
                "value": partial(
                    Naming.__join_with,
                    "",
                    _value,
                    lambda x: (x[0].upper() if x else ""),
                ),
                "regex": r"(?P<shorts_upper>[A-Z0-9]+)",
            },
            "%c": {
                "value": partial(Naming.camel_case, "_".join(_value)),
                "regex": (
                    r"(?P<strings_camel>[a-z]+"
                    r"((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?)"
                    # r"(?P<strings_camel>[a-z]+(?:[A-Z0-9]+[a-z0-9]+[A-Za-z0-9]*)*)"
                ),
            },
            "%-c": {
                "value": partial(Naming.pascal_case, "_".join(_value)),
                "cregex": "%p",
            },
            "%p": {
                "value": partial(Naming.pascal_case, "_".join(_value)),
                "regex": (
                    r"(?P<strings_pascal>[A-Z]"
                    r"([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|"
                    r"[a-z0-9]*[A-Z][A-Z0-9]*[a-z])["
                    r"A-Za-z0-9]*)"
                    # r"(?P<strings_pascal>(?:[A-Z][a-z0-9]+)(?:[A-Z]+[a-z0-9]*)*)"
                ),
            },
            "%k": {
                "value": partial(Naming.__join_with, "-", _value),
                "regex": r"(?P<strings_kebab>[a-z0-9]+(?:-[a-z0-9]+)*)",
            },
            "%K": {
                "value": partial(
                    Naming.__join_with, "-", _value, lambda x: x.upper()
                ),
                "regex": r"(?P<strings_kebab_upper>[A-Z0-9]+(?:-[A-Z0-9]+)*)",
            },
            "%-K": {
                "value": partial(
                    Naming.__join_with, "-", _value, lambda x: x.capitalize()
                ),
                "regex": (
                    r"(?P<strings_kebab_title>"
                    r"[A-Z][a-z0-9]+(?:-[A-Z]+[a-z0-9]*)*)"
                ),
            },
            "%f": {
                "value": partial(Naming.__join_with, "", _value),
                "regex": r"(?P<flats>[a-z0-9]+)",
            },
            "%F": {
                "value": partial(
                    Naming.__join_with, "", _value, lambda x: x.upper()
                ),
                "regex": r"(?P<flats_upper>[A-Z0-9]+)",
            },
            "%s": {
                "value": partial(Naming.__join_with, "_", _value),
                "regex": r"(?P<strings_snake>[a-z0-9]+(?:_[a-z0-9]+)*)",
            },
            "%S": {
                "value": partial(
                    Naming.__join_with, "_", _value, lambda x: x.upper()
                ),
                "regex": r"(?P<strings_snake_upper>[A-Z0-9]+(?:_[A-Z0-9]+)*)",
            },
            "%-S": {
                "value": partial(
                    Naming.__join_with, "_", _value, lambda x: x.capitalize()
                ),
                "regex": (
                    r"(?P<strings_snake_title>"
                    r"[A-Z][a-z0-9]+(?:_[A-Z]+[a-z0-9]*)*)"
                ),
            },
            "%v": {
                "value": partial(re.sub, r"[aeiou]", "", "".join(_value)),
                "regex": r"(?P<vowel>[b-df-hj-np-tv-z]+)",
            },
            "%V": {
                "value": partial(
                    re.sub, r"[AEIOU]", "", "".join(_value).upper()
                ),
                "regex": r"(?P<vowel_upper>[B-DF-HJ-NP-TV-Z]+)",
            },
        }

    @staticmethod
    def prepare_value(value: Optional[Union[str, List[str]]]) -> List[str]:
        if value is None:
            return [""]
        if isinstance(value, str):
            return Naming.__prepare_value(value)
        elif not isinstance(value, list) or any(
            not isinstance(v, str) for v in value
        ):
            raise FormatterValueError(
                f"Naming formatter does not support for value, {value!r}."
            )
        return value

    @staticmethod
    def pascal_case(snake_case: str) -> str:
        """Return a string value with pascal case that reference by
        `inflection`.
        """
        return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), snake_case)

    @staticmethod
    def camel_case(snake_case: str) -> str:
        """Return a string value with camel case with lower case first
        letter.
        """
        return (
            (snake_case[0].lower() + Naming.pascal_case(snake_case)[1:])
            if snake_case
            else ""
        )

    @staticmethod
    def __join_with(
        by: str,
        values: List[str],
        func: Optional[Callable[[str], str]] = None,
    ) -> str:
        """Return string value that join with any separate string"""
        return by.join(map(func, values)) if func else by.join(values)

    @staticmethod
    def __prepare_value(value: str) -> List[str]:
        """Return list of word that split from input value string"""
        result: str = re.sub(r"[^\-.\w\s]+", "", value)
        return re.sub(r"[\-._\s]", " ", result).strip().split()

    @staticmethod
    def __split_pascal_case(value: str) -> List[str]:
        return (
            "".join([f" {c.lower()}" if c.isupper() else c for c in value])
            .strip()
            .split()
        )

    def __sub__(self, other):  # type: ignore # no cov
        return NotImplemented

    def __rsub__(self, other):  # type: ignore # no cov
        return NotImplemented


SIZE: Tuple[str, ...] = (
    "B",
    "KB",
    "MB",
    "GB",
    "TB",
    "PB",
    "EB",
    "ZB",
    "YB",
)


class Storage(Formatter):
    """Storage object for register process that implement formatter and
    parser.
    """

    base_fmt: str = "%b"

    __slots__ = (
        "bit",
        "byte",
        "storage",
    )

    @property
    def value(self) -> int:
        return int(self.string)

    @property
    def string(self) -> str:
        return self.bit  # type: ignore[no-any-return]

    @property
    def priorities(self) -> ReturnPrioritiesType:
        return {
            "bit": {
                "value": lambda x: x,
                "level": 1,
            },
            "byte": {
                "value": lambda x: self.to_byte(x, "B"),
                "level": 1,
            },
            "byte_kilo": {
                "value": lambda x: self.to_byte(x, "KB"),
                "level": 1,
            },
            "byte_mega": {
                "value": lambda x: self.to_byte(x, "MB"),
                "level": 1,
            },
            "byte_giga": {
                "value": lambda x: self.to_byte(x, "GB"),
                "level": 1,
            },
            "byte_tera": {
                "value": lambda x: self.to_byte(x, "TB"),
                "level": 1,
            },
            "byte_peta": {
                "value": lambda x: self.to_byte(x, "PB"),
                "level": 1,
            },
            "byte_exa": {
                "value": lambda x: self.to_byte(x, "EB"),
                "level": 1,
            },
            "byte_zetta": {
                "value": lambda x: self.to_byte(x, "ZB"),
                "level": 1,
            },
            "byte_yotta": {
                "value": lambda x: self.to_byte(x, "YB"),
                "level": 1,
            },
            "bit_default": {
                "value": self._from_byte,
                "level": 0,
            },
            "byte_default": {
                "value": self._from_bit,
                "level": 0,
            },
        }

    @staticmethod
    def formatter(storage: Optional[int] = None) -> ReturnFormattersType:
        """Generate formatter that support mapping formatter,

        %b  : Bit format
        %B  : Byte format
        %K  : Kilo-Byte format
        %M  : Mega-Byte format
        %G  : Giga-Byte format
        %T  : Tera-Byte format
        %P  : Peta-Byte format
        %E  : Exa-Byte format
        %Z  : Zetta-Byte format
        %Y  : Yotta-Byte format

        """
        size: int = Storage.prepare_value(storage)
        return {
            "%b": {
                "value": lambda: str(size),
                "regex": r"(?P<bit>[0-9]*)",
            },
            "%B": {
                "value": lambda: f"{round(size / 8)}B",
                "regex": r"(?P<byte>[0-9]*B)",
            },
            "%K": {
                "value": partial(Storage.bit2byte, size, "KB"),
                "regex": r"(?P<byte_kilo>[0-9]*KB)",
            },
            "%M": {
                "value": partial(Storage.bit2byte, size, "MB"),
                "regex": r"(?P<byte_mega>[0-9]*MB)",
            },
            "%G": {
                "value": partial(Storage.bit2byte, size, "GB"),
                "regex": r"(?P<byte_giga>[0-9]*GB)",
            },
            "%T": {
                "value": partial(Storage.bit2byte, size, "TB"),
                "regex": r"(?P<byte_tera>[0-9]*TB)",
            },
            "%P": {
                "value": partial(Storage.bit2byte, size, "PB"),
                "regex": r"(?P<byte_peta>[0-9]*PB)",
            },
            "%E": {
                "value": partial(Storage.bit2byte, size, "EB"),
                "regex": r"(?P<byte_exa>[0-9]*EB)",
            },
            "%Z": {
                "value": partial(Storage.bit2byte, size, "ZB"),
                "regex": r"(?P<byte_zetta>[0-9]*ZB)",
            },
            "%Y": {
                "value": partial(Storage.bit2byte, size, "YB"),
                "regex": r"(?P<byte_yotta>[0-9]*YB)",
            },
        }

    @staticmethod
    def prepare_value(value: Optional[int]) -> int:
        if value is None:
            return 0
        if not can_int(value) or (int(value) < 0):
            raise FormatterValueError(
                f"Storage formatter does not support for value, {value!r}."
            )
        return int(value)

    def _from_byte(self) -> str:
        return str(int(self.byte or "0") * 8)

    def _from_bit(self) -> str:
        return str(round(int(self.bit or "0") / 8))

    @staticmethod
    def bit2byte(value: int, order: str) -> str:
        p = math.pow(1024, SIZE.index(order))
        return f"{(round((value / 8) / p))}{order}"

    @staticmethod
    def to_byte(value: str, order: str) -> str:
        p = math.pow(1024, SIZE.index(order))
        return f"{round(int(value.replace(order, '')) * p)}"


Constant = TypeVar("Constant", bound="__BaseConstant")


class __BaseConstant(Formatter):
    """Constant object for register process that implement formatter and
    parser.
    """

    base_fmt: str = "%%"

    __slots__: Tuple[str, ...] = ("_constant",)

    @classmethod
    def passer(cls, value: Any) -> NoReturn:
        raise NotImplementedError(
            "The Constant class does not support for passing value to this "
            "class initialization."
        )

    @classmethod
    def parse(cls, value: str, fmt: Optional[str] = None) -> Formatter:
        if fmt is None:
            raise NotImplementedError(
                "The Constant class does not support for default format string "
                "when parsing with this unknown format value."
            )
        return super().parse(value, fmt)

    def __init__(
        self,
        formats: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.formatter():
            raise NotImplementedError(
                "The Constant object should define the `cls.base_formatter` "
                "before make a instance."
            )
        super().__init__(formats=formats, set_std_value=False)

        # Set constant property
        self._constant: List[str] = [
            getter for v in self.__slots__ if (getter := getattr(self, v, None))
        ]

        # Set standard property by default is string value or `self.string`
        setattr(
            self,
            self.__class__.__name__.lower(),
            str(self.string),
        )

    @property
    def value(self) -> List[str]:
        return self._constant

    @property
    def string(self) -> str:
        return "|".join(self._constant)

    @property
    def priorities(self) -> ReturnPrioritiesType:
        raise NotImplementedError(
            "Please implement priorities property for this sub-constant "
            "formatter class"
        )

    @staticmethod
    def formatter(
        value: Optional[List[str]] = None,
    ) -> ReturnFormattersType:
        raise NotImplementedError(
            "Please implement formatter staticmethod for this sub-constant "
            "formatter class"
        )

    def __lt__(self, other: Formatter) -> bool:
        return not (self.value.__eq__(other.value))

    def __gt__(self, other: Formatter) -> bool:
        return not (self.value.__eq__(other.value))

    @staticmethod
    def prepare_value(value: Any) -> Any:
        return value

    def __add__(self, other):  # type: ignore # no cov
        return NotImplemented

    def __sub__(self, other):  # type: ignore # no cov
        return NotImplemented

    def __rsub__(self, other):  # type: ignore # no cov
        return NotImplemented


def dict2const(
    fmt: Dict[str, str],
    name: str,
    *,
    base_fmt: Optional[str] = None,
) -> ConstantType:
    """Constant function constructor that receive the dict of format string
    value and constant value.

    :param fmt:
    :param name:
    :param base_fmt:

    :rtype: ConstantType
    """
    _base_fmt: str = base_fmt or "".join(fmt.keys())

    class CustomConstant(__BaseConstant):
        base_fmt: str = _base_fmt

        __qualname__ = name

        __slots__: Tuple[str, ...] = (
            name.lower(),
            "_constant",
            *[convert_fmt_str(f) for f in fmt],
        )

        def __repr__(self) -> str:
            _bf: str = "|".join(self.__search_fmt(c) for c in self._constant)
            return (
                f"<{self.__class__.__name__}"
                f".parse('{self.string}', "
                f"'{_bf}')>"
            )

        @staticmethod
        def formatter(  # type: ignore[override]
            v: Optional[str] = None,
        ) -> ReturnFormattersType:
            _ = CustomConstant.prepare_value(v)
            return {
                f: {
                    "regex": f"(?P<{convert_fmt_str(f)}>{fmt[f]})",
                    "value": fmt[f],
                }
                for f in fmt.copy()
            }

        @property
        def priorities(self) -> ReturnPrioritiesType:
            return {
                convert_fmt_str(f): {"value": lambda x: x, "level": 1}
                for f in fmt
            }

        def values(self, value: Optional[Any] = None) -> Dict[str, str]:
            """Return the constant values"""
            _ = self.prepare_value(value)
            return fmt

        def __search_fmt(self, value: str) -> str:
            """Return the first format that equal to an input string value."""
            return [k for k, v in iter(self.values().items()) if v == value][0]

    CustomConstant.__name__ = name
    return CustomConstant


def make_const(
    name: Optional[str] = None,
    formatter: Optional[Union[Dict[str, str], Formatter]] = None,
    *,
    fmt: Optional[FormatterType] = None,
    value: Optional[Any] = None,
) -> ConstantType:
    """Constant function constructor"""
    base_fmt: Optional[str] = None
    _fmt: Dict[str, str]
    if formatter is None:
        if fmt is None or not inspect.isclass(fmt):
            raise FormatterArgumentError(
                "formatter",
                "The Constant constructor function must pass formatter nor fmt "
                "arguments.",
            )
        name = f"{fmt.__name__}Const"
        _fmt = fmt().values(value=value)
        base_fmt = fmt.base_fmt
    elif isinstance(formatter, Formatter):
        return formatter.to_const()
    else:
        _fmt = formatter

    if not name:
        raise FormatterArgumentError("name", "The Constant want name arguments")
    return dict2const(_fmt, name=name, base_fmt=base_fmt)


EnvConstant: ConstantType = make_const(
    name="EnvConstant",
    formatter={
        "%d": "development",
        "%-d": "dev",
        "%s": "sit",
        "%-s": "sit",
        "%u": "uat",
        "%-u": "uat",
        "%p": "production",
        "%-p": "prd",
        "%t": "test",
        "%-t": "test",
        "%b": "sandbox",
        "%-b": "box",
        "%c": "poc",
    },
)


@final
class GenFormatValue(TypedDict):
    fmt: str


@final
class PVParseValue(TypedDict):
    fmt: str
    value: str
    props: Dict[str, str]


ReturnGroupGenFormatType = Dict[str, GenFormatValue]
ReturnPVParseType = Dict[str, PVParseValue]


FormatterGroup = TypeVar("FormatterGroup", bound="__FormatterGroup")
GroupValue = Dict[str, FormatterType]


class __FormatterGroup:
    """Group of any Formatters together with dynamic group naming like
    timestamp for Datetime formatter object.

    :param formats: A mapping value of priority attribute data.
    :type formats: Optional[dict](=None)

    .. class attributes::

        - base_groups: GroupValue

    .. attributes::

        - groups

    .. methods::

        -

        This class is abstract class for any formatter group class.
    """

    # This value must reassign from child class
    base_groups: GroupValue = {}

    def __init_subclass__(cls: FormatterGroupType, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if not cls.base_groups:
            raise NotImplementedError(
                "Please implement base_groups class property for this "
                "sub-formatter group class."
            )

    @classmethod
    def parse(
        cls,
        value: str,
        fmt: str,
    ) -> __FormatterGroup:
        """Parse formatter by generator values like timestamp, version,
        or serial.

        :param value:
        :type value: str
        :param fmt:
        :type fmt: str

        :rtype: Dict[str, Formatter]
        """
        parser_rs: ReturnPVParseType = cls.__parse(value, fmt)
        rs: Dict[str, Dict[str, str]] = defaultdict(dict)
        for group in parser_rs:
            group_origin: str = group.split("__")[0]
            rs[group_origin] = {**parser_rs[group]["props"], **rs[group_origin]}
        return cls(formats=rs)

    @classmethod
    def __parse(
        cls,
        value: str,
        fmt: str,
    ) -> ReturnPVParseType:
        _fmt, _fmt_getter = cls.gen_format(fmt=fmt)
        if not (_search := re.search(rf"^{_fmt}$", value)):
            raise FormatterGroupArgumentError(
                "format",
                f"{value!r} does not match with the format: '^{_fmt}$'",
            )

        _search_dict: Dict[str, str] = _search.groupdict()
        rs: ReturnPVParseType = {}
        for name in iter(_fmt_getter.copy()):
            rs[name] = {
                "fmt": _fmt_getter[name]["fmt"],
                "value": _search_dict.pop(name),
                "props": {
                    k.replace(name, "", 1): _search_dict.pop(k)
                    for k in filter(
                        lambda x: x.startswith(name),
                        _search_dict.copy(),
                    )
                },
            }
        return rs

    @classmethod
    def gen_format(cls, fmt: str) -> Tuple[str, ReturnGroupGenFormatType]:
        """Generate format string value to regular expression value that able
        to search with any input value.

        :param fmt: a format string value pass from input argument.
        :type fmt: str
        """
        fmt_getter: ReturnGroupGenFormatType = {}
        for group, formatter in cls.base_groups.items():
            for _index, fmt_match in enumerate(
                re.finditer(
                    rf"(?P<found>{{{group}:?(?P<format>[^{{}}]+)?}})",
                    fmt,
                ),
                start=0,
            ):
                # Format Dict Example:
                # {'name': '{timestamp:%Y_%m_%d}', 'format': '%Y_%m_%d'}
                fmt_dict: Dict[str, str] = fmt_match.groupdict()
                fmt_str: str
                if not (fmt_str := fmt_dict["format"]):
                    fmt_str = formatter.base_fmt
                group_index: str = f"{group}__{_index}"
                fmt_re = formatter.gen_format(
                    fmt_str,
                    prefix=group_index,
                    suffix=f"{_index}",
                )
                fmt = fmt.replace(
                    fmt_dict["found"],
                    f"(?P<{group_index}>{fmt_re})",
                    1,
                )
                fmt_getter[group_index] = {"fmt": fmt_str}
        return fmt, fmt_getter

    def format(self, fmt: str) -> str:
        """Return string value that was filled by the input format pattern
        argument.

        :param fmt: a string format value
        :type fmt: str
        """
        for fmt_match in re.finditer(
            r"(?P<found>{(?P<group>\w+):?(?P<format>[^{}]+)?})", fmt
        ):
            # Format Dict Example:
            # {
            #   'name': '{timestamp:%Y_%m_%d}',
            #   'group': 'timestamp',
            #   'format': '%Y_%m_%d'
            # }
            fmt_dict: Dict[str, str] = fmt_match.groupdict()
            if (group := fmt_dict["group"]) not in self.base_groups:
                raise FormatterGroupValueError(
                    f"This group, {group!r}, does not set on `cls.base_groups`."
                )
            formatter: Formatter = self.groups[group]
            fmt_str: str
            if not (fmt_str := fmt_dict["format"]):
                fmt_str = formatter.base_fmt

            try:
                fmt = fmt.replace(
                    fmt_dict["found"],
                    formatter.format(fmt=fmt_str),
                    1,
                )
            except FormatterKeyError as err:
                raise FormatterGroupArgumentError(
                    "format", f"{err} in {fmt_dict['found']}"
                ) from err
        return fmt

    def __init__(
        self,
        formats: Union[
            Dict[str, Dict[str, str]],
            Dict[str, Formatter],
            Any,
        ],
    ) -> None:
        """Main initialization get the formatter value, a mapping of name
        and formatter from input argument and generate the necessary
        attributes for define the value of this formatter group object.
        """
        self.groups: Dict[str, Formatter] = {
            group: fmt() for group, fmt in self.base_groups.items()
        }
        for k, v in formats.items():
            if k not in self.base_groups:
                raise FormatterGroupValueError(
                    f"{self.__class__.__name__} does not support for this "
                    f"group name, {k!r}."
                )
            self.groups[k] = self.__construct_groups(k, v)

    def __construct_groups(
        self,
        group: str,
        v: Union[Dict[str, str], Formatter, Any],
    ) -> Formatter:
        if isinstance(v, Formatter):
            return v
        elif isinstance(v, dict):
            return self.base_groups[group](v)
        return self.base_groups[group].passer(v)

    def __repr__(self) -> str:
        values: List[str] = []
        fmts: List[str] = []
        for group in self.base_groups:
            formatter: Formatter = self.groups[group]
            values.append(formatter.string)
            fmts.append(formatter.base_fmt)
        return (
            f"<{self.__class__.__name__}"
            f".parse(value={'_'.join(values)!r}, "
            f"fmt={'_'.join(fmts)!r})>"
        )

    def __str__(self) -> str:
        return ", ".join(v.string for v in self.groups.values())

    def adjust(self, values: Dict[str, Any]) -> __FormatterGroup:  # no cov
        _keys: List[str] = [
            f"{k!r}" for k in values if k not in self.base_groups
        ]
        if _keys:
            raise FormatterGroupValueError(
                f"Key of values, {', '.join(_keys)}, does not support for this "
                f"{self.__class__}."
            )
        _groups: Dict[str, Formatter] = {
            k: (fmt + values[k]) if k in values else fmt
            for k, fmt in self.groups.items()
        }
        return self.__class__(_groups)


def make_group(group: GroupValue) -> FormatterGroupType:
    # Validate argument group that should contain ``FormatterType``
    for _ in group.values():
        try:
            if not issubclass(_, Formatter):
                raise ValueError(
                    f"Make group constructor function want group with type, "
                    f"Dict[str, FormatterType], not {_.__name__!r}."
                )
        except TypeError as err:
            raise FormatterGroupArgumentError(
                "group",
                (
                    f"Make group constructor function want group with type, "
                    f"Dict[str, FormatterType], not instance of "
                    f"{_.__class__.__name__!r}."
                ),
            ) from err

    name: str = f'{"".join(_.__name__ for _ in group.values())}Group'

    @total_ordering
    class CustomGroup(__FormatterGroup):
        base_groups: GroupValue = group

        __qualname__ = name

        def __hash__(self) -> int:
            return hash(self.__str__())

        def __eq__(self, other: Union[CustomGroup, Any]) -> bool:
            return isinstance(other, self.__class__) and all(
                self.groups[g] == other.groups[g] for g in self.base_groups
            )

        def __gt__(self, other: Union[CustomGroup, Any]) -> bool:
            if isinstance(other, self.__class__):
                return any(
                    self.groups[g].__gt__(other.groups[g])
                    for g in self.base_groups
                ) and all(
                    not self.groups[g].__lt__(other.groups[g])
                    for g in self.base_groups
                )
            return NotImplemented

        def __lt__(self, other: Union[CustomGroup, Any]) -> bool:
            if isinstance(other, self.__class__):
                return any(
                    self.groups[g].__lt__(other.groups[g])
                    for g in self.base_groups
                ) and all(
                    not self.groups[g].__gt__(other.groups[g])
                    for g in self.base_groups
                )
            return NotImplemented

    CustomGroup.__name__ = name
    return CustomGroup


__all__ = (
    # Formatter
    "Formatter",
    "FormatterType",
    "ReturnPrioritiesType",
    "ReturnFormattersType",
    "Serial",
    "Datetime",
    "Version",
    "Naming",
    "Storage",
    "ConstantType",
    "Constant",
    "EnvConstant",
    "dict2const",
    "make_const",
    # Formatter Group
    "FormatterGroup",
    "FormatterGroupType",
    "make_group",
)
