# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the Serial formatter object.
"""
import unittest

import fmtutil.formatter as fmt
from fmtutil.exceptions import FormatterKeyError


class SerialTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sr = fmt.Serial({"number": "781"})
        self.sr_default: fmt.Formatter = fmt.Serial()
        self.sr_p: fmt.Formatter = fmt.Serial.parse("009", "%p")
        self.sr_p2: fmt.Formatter = fmt.Serial.parse("00001101", "%b")

    def test_serial_regex(self):
        self.assertDictEqual(
            {
                "%n": "(?P<number>[0-9]*)",
                "%p": "(?P<number_pad>[0-9]{3})",
                "%b": "(?P<number_binary>[0-1]*)",
            },
            fmt.Serial.regex(),
        )

    def test_serial_formatter(self):
        formatter = fmt.Serial.formatter(serial=512)
        regex = fmt.Serial.regex()
        self.assertDictEqual(
            {
                "%b": {
                    "regex": "(?P<number_binary>[0-1]*)",
                    "value": "1000000000",
                },
                "%n": {"regex": "(?P<number>[0-9]*)", "value": "512"},
                "%p": {"regex": "(?P<number_pad>[0-9]{3})", "value": "512"},
            },
            {
                i: {
                    "regex": regex[i],
                    "value": fmt.caller(formatter[i]["value"]),
                }
                for i in formatter
            },
        )

    def test_serial_formatter_raise(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.Serial.formatter(1.23)
        self.assertTrue(
            "Serial formatter does not support for value, 1.23."
            in str(context.exception)
        )

        # fmt.Serial.formatter("a")

    def test_serial_properties(self):
        self.assertEqual("<Serial.parse('781', '%n')>", self.sr.__repr__())
        self.assertEqual(hash(self.sr.string), self.sr.__hash__())

        self.assertEqual(9, self.sr_p.value)
        self.assertEqual("9", self.sr_p.string)

        self.assertEqual(13, self.sr_p2.value)
        self.assertEqual("13", self.sr_p2.string)

        self.assertEqual(0, self.sr_default.value)
        self.assertEqual("0", self.sr_default.string)

    def test_serial_format(self):
        self.assertEqual("00001001", self.sr_p.format("%b"))
        self.assertEqual("009", self.sr_p.format("%p"))

        self.assertEqual("00001101", self.sr_p2.format("%b"))
        self.assertEqual("013", self.sr_p2.format("%p"))

        self.assertEqual("00000000", self.sr_default.format("%b"))
        self.assertEqual("000", self.sr_default.format("%p"))

        with self.assertRaises(FormatterKeyError) as context:
            self.sr_default.format("%Z")
        self.assertTrue(
            "the format: '%Z' does not support for 'Serial'"
            in str(context.exception)
        )

    def test_serial_order(self):
        self.assertTrue(self.sr_p <= self.sr_p2)
        self.assertTrue(self.sr_p < self.sr_p2)
        self.assertFalse(self.sr_p == self.sr_p2)
        self.assertFalse(self.sr_p >= self.sr_p2)
        self.assertFalse(self.sr_p > self.sr_p2)

    def test_level_compare(self):
        self.assertEqual(1, self.sr_p.level.value)
        self.assertEqual(0, self.sr_default.level.value)
        self.assertTrue(self.sr_p.level == self.sr_p2.level)
        self.assertFalse(self.sr_default.level == self.sr_p2.level)
        self.assertTrue(self.sr_default.level < self.sr_p2.level)
        self.assertListEqual([True], self.sr_p.level.slot)
        self.assertListEqual([False], self.sr_default.level.slot)

    def test_serial_operation(self):
        self.assertEqual(fmt.Serial({"number": "790"}), self.sr + self.sr_p)
        self.assertEqual(fmt.Serial({"number": "786"}), self.sr + 5)
        self.assertEqual(fmt.Serial({"number": "786"}), 5 + self.sr)

        self.assertEqual(fmt.Serial({"number": "761"}), self.sr - 20)
        self.assertEqual(fmt.Serial({"number": "772"}), self.sr - self.sr_p)
        self.assertEqual(1219, 2000 - self.sr)
        self.assertEqual(1219.2, (2000.20 - self.sr))

        with self.assertRaises(TypeError) as context:
            (self.sr + 5.1)
        self.assertEqual(
            "unsupported operand type(s) for +: 'Serial' and 'float'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (self.sr + "1.0")
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (self.sr + "a")
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (5.1 + self.sr)
        self.assertEqual(
            "unsupported operand type(s) for +: 'float' and 'Serial'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            ("1.0" + self.sr)
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            ("a" + self.sr)
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (self.sr - 800)
        self.assertEqual(
            "unsupported operand type(s) for -: 'Serial' and 'int'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (self.sr - 20.5)
        self.assertEqual(
            "unsupported operand type(s) for -: 'Serial' and 'float'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            ("234" - self.sr)
        self.assertEqual(
            "unsupported operand type(s) for -: 'str' and 'Serial'",
            str(context.exception),
        )
