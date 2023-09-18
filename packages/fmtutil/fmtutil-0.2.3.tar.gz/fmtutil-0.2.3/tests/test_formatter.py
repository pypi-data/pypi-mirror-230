# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the formatter object.
"""
import unittest
from abc import ABC
from typing import Any, Dict, Optional, Type

import fmtutil.formatter as fmt


class SlotLevelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sl = fmt.SlotLevel(level=5)
        self.sl.update(numbers=(2, 3, 4))

    def test_slot_level_properties(self):
        self.assertEqual("<SlotLevel(level=5)>", self.sl.__repr__())
        self.assertEqual("5", self.sl.__str__())
        self.assertEqual(hash(tuple(self.sl.slot)), self.sl.__hash__())
        self.assertEqual(3, self.sl.count)
        self.assertEqual(9, self.sl.value)

    def test_slot_level_update_failed(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.SlotLevel(level=5).update(numbers=(6,), strict=True)
        self.assertTrue(
            (
                "number for update the slot level object "
                "does not in range of 0 and 5."
            )
            in str(context.exception)
        )
        self.assertEqual(
            "<SlotLevel(level=5)>",
            fmt.SlotLevel(level=5)
            .update(numbers=(6,), strict=False)
            .__repr__(),
        )


class PriorityDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        ...

    @staticmethod
    def caller(x):
        _ = x
        return 1

    def test_caller(self):
        self.assertEqual(1, self.caller("anythings"))

    def test_init_data(self):
        self.assertEqual(
            "PriorityData(level=5)",
            fmt.PriorityData(**{"value": self.caller, "level": 5}).__repr__(),
        )


class FormatterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        class WrongFormatter(fmt.Formatter):
            base_fmt: str = "%n"

            base_attr_prefix: str = "sr"

            __slots__ = (
                "_sr_number",
                "_sr_serial",
            )

            @property
            def value(self) -> int:  # pragma: no cover
                raise NotImplementedError

            @property
            def string(self) -> str:  # pragma: no cover
                raise NotImplementedError

            @property
            def priorities(self) -> Dict[str, dict]:  # pragma: no cover
                raise NotImplementedError

            @staticmethod
            def formatter(
                serial: Optional[int] = None,
            ) -> Dict[str, Dict[str, str]]:
                _value: str = str(serial or 0)
                return {
                    "%n": {
                        "value": _value,
                        "wrong_regex": r"(?P<number>[0-9]*)",
                    },
                }

            @staticmethod
            def prepare_value(value: Any) -> Any:
                return value

        class NotImpPriority(fmt.Formatter, ABC):
            base_fmt: str = "%n"

            base_attr_prefix: str = "sr"

            __slots__ = (
                "_sr_number",
                "_sr_serial",
            )

            @property
            def value(self) -> int:  # pragma: no cover
                return 1

            @property
            def string(self) -> str:  # pragma: no cover
                return "Demo"

            @staticmethod
            def formatter(
                serial: Optional[int] = None,
            ) -> Dict[str, Dict[str, str]]:
                _value: str = str(serial or 0)
                return {
                    "%n": {
                        "value": _value,
                        "wrong_regex": r"(?P<number>[0-9]*)",
                    },
                }

        class ValidateFormatter(fmt.Naming):
            @property
            def validate(self) -> bool:
                return False

        self.wrong_fmt_cls = WrongFormatter
        self.not_imp_priority_cls = NotImpPriority
        self.validate_fmt_cls = ValidateFormatter

    def test_base_formatter_properties(self):
        with self.assertRaises(TypeError) as context:
            fmt.Formatter()
        print(str(context.exception))
        self.assertTrue(
            (
                "Can't instantiate abstract class Formatter with abstract "
                "methods formatter, prepare_value, priorities, string, value"
            )
            in str(context.exception)
        )

    def test_base_formatter_init_with_fmt(self):
        with self.assertRaises(TypeError) as context:
            fmt.Formatter({"month": 1})
        self.assertTrue(
            (
                "Can't instantiate abstract class Formatter with abstract "
                "methods formatter, prepare_value, priorities, string, value"
            )
            in str(context.exception)
        )

    def test_base_formatter_parse_without_fmt(self):
        with self.assertRaises(NotImplementedError) as context:
            fmt.Formatter.parse("dummy")
        self.assertTrue(
            "This Formatter class does not set default format string value."
            in str(context.exception)
        )

    def test_base_formatter_parse_with_fmt(self):
        with self.assertRaises(NotImplementedError) as context:
            fmt.Formatter.parse("dummy", "%Z")
        self.assertTrue(
            (
                "Please implement formatter static method "
                "for this sub-formatter class"
            )
            in str(context.exception)
        )

    def test_base_formatter_prepare_value(self):
        with self.assertRaises(NotImplementedError) as context:
            fmt.Formatter.prepare_value("Demo")
        self.assertTrue(
            (
                "Please implement prepare_value static method for this "
                "sub-formatter class."
            )
            in str(context.exception)
        )

    def test_new_format_with_wrong_formatter(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            self.wrong_fmt_cls.regex()
        self.assertTrue(
            "formatter does not contain `regex` or `cregex` "
            "in dict value" in str(context.exception)
        )

    def test_new_format_without_priorities(self):
        with self.assertRaises(TypeError) as context:
            self.not_imp_priority_cls()
        # TODO: Change merge asserts together when move to python39
        #  (This is issue of python38, error statement have `s` after `method`)
        self.assertTrue(
            "Can't instantiate abstract class NotImpPriority "
            "with abstract method" in str(context.exception)
        )
        self.assertTrue("priorities" in str(context.exception))

    def test_new_validate_error(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            self.validate_fmt_cls()
        self.assertTrue(
            "Parsing value does not valid from validator"
            in str(context.exception)
        )


class TypeConstructFormatterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        def value(_s) -> int:  # no cov
            return int(_s.string)

        def string(_s) -> str:  # no cov
            return _s.bit

        def validate(_s) -> bool:
            if _s.bit != 0 and _s.byte != 0 and _s.bit != _s.byte:
                return False
            if _s.bit == 0 and _s.byte != 0:
                _s.bit = _s.byte
            elif _s.bit != 0 and _s.byte == 0:
                _s.byte = _s.bit
            return True

        def priorities(_s):  # no cov
            return {
                "bit": {
                    "value": lambda x: int(x),
                    "level": 1,
                },
                "byte": {
                    "value": lambda x: (int(x.replace("B", "")) * 8),
                    "level": 1,
                },
                "bit_default": {"value": _s.default(0)},
                "byte_default": {"value": _s.default(0)},
            }

        def formatter(v: Optional[Any] = None):  # no cov
            size: int = v or 0
            return {
                "%b": {
                    "value": lambda: str(size),
                    "regex": r"(?P<bit>[0-9]*)",
                },
                "%B": {
                    "value": lambda: f"{str(round(size / 8))}B",
                    "regex": r"(?P<byte>[0-9]*B)",
                },
            }

        def formatter_raise(v: Optional[Any] = None):  # no cov
            size: int = v or 0
            return {
                "%b": {
                    "value": lambda: str(size),
                    "regex": r"([0-9]*)",
                },
                "%B": {
                    "value": lambda: f"{str(round(size / 8))}B",
                    "regex": r"([0-9]*B)",
                },
            }

        def formatter_raise02(v: Optional[Any] = None):  # no cov
            size: int = v or 0
            return {
                "%b": {
                    "value": lambda: str(size),
                    "regex": r"(?P<bit>[0-9]*)",
                },
                "%B": {
                    "value": lambda: f"{str(round(size / 8))}B",
                    "regex": r"(?P<byte>[0-9]*B)",
                },
                "%M": {
                    "value": lambda: f"{str(round(size / 8 / 8))}MB",
                    "cregex": "%Z",
                },
            }

        def prepare_value(v: Any) -> Any:
            return v

        self.cst_with_type_cls: Type[fmt.Formatter] = type(  # no cov
            "Storage",
            (fmt.Formatter,),
            {
                "__slots__": (
                    "bit",
                    "byte",
                    "storage",
                ),
                "base_fmt": "%b",
                "string": property(string),
                "value": property(value),
                "validate": property(validate),
                "priorities": property(priorities),
                "formatter": staticmethod(formatter),
                "prepare_value": staticmethod(prepare_value),
            },
        )

        class TypeConstructFormatterMeta(fmt.Formatter, ABC):  # no cov
            __slots__ = (
                "bit",
                "byte",
                "storage",
            )
            base_fmt = "%b"

        self.cst_with_type_cls2: Type[fmt.Formatter] = type(  # no cov
            "Storage",
            (TypeConstructFormatterMeta,),
            {
                "string": property(string),
                "value": property(value),
                "validate": property(validate),
                "priorities": property(priorities),
                "formatter": staticmethod(formatter),
                "prepare_value": staticmethod(prepare_value),
            },
        )

        self.cst_with_type_cls_raise: Type[fmt.Formatter] = type(  # no cov
            "Storage",
            (TypeConstructFormatterMeta,),
            {
                "string": property(string),
                "value": property(value),
                "validate": property(validate),
                "priorities": property(priorities),
                "formatter": staticmethod(formatter_raise),
                "prepare_value": staticmethod(prepare_value),
            },
        )

        self.cst_with_type_cls_raise02: Type[fmt.Formatter] = type(  # no cov
            "Storage",
            (TypeConstructFormatterMeta,),
            {
                "string": property(string),
                "value": property(value),
                "validate": property(validate),
                "priorities": property(priorities),
                "formatter": staticmethod(formatter_raise02),
                "prepare_value": staticmethod(prepare_value),
            },
        )

    def test_type_formatter_init(self):
        self.assertEqual(
            "250B",
            self.cst_with_type_cls({"bit": "2000"}).format("%B"),
        )
        self.assertEqual(
            "250B",
            self.cst_with_type_cls2({"bit": "2000"}).format("%B"),
        )

    def test_type_formatter_regex(self):
        with self.assertRaises(fmt.FormatterArgumentError) as context:
            self.cst_with_type_cls_raise02.regex()
        self.assertTrue(
            (
                "with 'format', format cregex string that contain %Z regex "
                "does not found."
            )
            in str(context.exception)
        )

    def test_type_formatter_parse(self):
        self.assertEqual(
            2000,
            self.cst_with_type_cls2.parse("250B", "%B").value,
        )
        self.assertEqual(
            10000,
            self.cst_with_type_cls2.parse("10000", "%b").value,
        )

        with self.assertRaises(fmt.FormatterValueError) as context:
            self.cst_with_type_cls_raise.parse("2000B", "%B")
        self.assertTrue(
            (
                "Regex format string does not set group name for parsing value "
                "to its class."
            )
            in str(context.exception)
        )
