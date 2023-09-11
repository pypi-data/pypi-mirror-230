# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Define Errors Object for formatter
"""
from __future__ import annotations

from typing import Tuple, Union


class BaseError(Exception):
    """Base Error Object that use for catch any errors statement of
    all step in this package.
    """


class FormatterError(BaseError):
    """Core Base Error object for formatter"""


class FormatterNotFoundError(FormatterError):
    """Error raise for a method not found the config file or data."""


class FormatterTypeError(FormatterError):
    """Error raise for typing does not match or support."""


class FormatterValueError(FormatterError):
    """Error raise for value does not valid"""


class FormatterKeyError(FormatterError):
    """Error raise for key does not exist"""


class FormatterArgumentError(FormatterError):
    """Error raise for a wrong configuration argument.

    >>> FormatterArgumentError(argument='demo', message='does not support')
    FormatterArgumentError("with 'demo', does not support")

    :param argument: argument of this error that raise to client
    :type argument: Union[str, tuple]
    :param message: string message of this error
    :type message: str
    """

    def __init__(self, argument: Union[str, Tuple[str, ...]], message: str):
        """Main Initialization that merge the argument and message input values
        with specific content message together like

            `__class__` with `argument`, `message`
        """
        _argument: str
        if isinstance(argument, tuple):
            _last_arg: str = str(argument[-1])
            _argument = (
                (
                    ", ".join(f"{x!r}" for x in argument[:-1])
                    + f", and {_last_arg!r}"
                )
                if len(argument) > 1
                else f"{_last_arg!r}"
            )
        else:
            _argument = f"{argument!r}"
        super().__init__(f"with {_argument}, {message}")


class FormatterGroupError(FormatterError):
    """Core Base Error object for formatter group"""


class FormatterGroupNotFoundError(FormatterNotFoundError):
    """Error raise for a method not found the config file or data."""


class FormatterGroupTypeError(FormatterTypeError):
    """Error raise for typing does not match or support."""


class FormatterGroupValueError(FormatterValueError):
    """Error raise for value does not valid"""


class FormatterGroupKeyError(FormatterKeyError):
    """Error raise for key does not exist"""


class FormatterGroupArgumentError(FormatterArgumentError):
    """Error raise for a wrong configuration argument."""
