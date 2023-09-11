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


class StorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.st = fmt.Storage({"bit": "10481"})
        self.st_default: fmt.Formatter = fmt.Storage()
        self.st_p: fmt.Formatter = fmt.Storage.parse("10353B", "%B")
        self.st_p2: fmt.Formatter = fmt.Storage.parse("135005", "%b")

    def test_storage_regex(self):
        self.assertDictEqual(
            {
                "%b": "(?P<bit>[0-9]*)",
                "%B": "(?P<byte>[0-9]*B)",
                "%K": "(?P<byte_kilo>[0-9]*KB)",
                "%M": "(?P<byte_mega>[0-9]*MB)",
                "%G": "(?P<byte_giga>[0-9]*GB)",
                "%T": "(?P<byte_tera>[0-9]*TB)",
                "%P": "(?P<byte_peta>[0-9]*PB)",
                "%E": "(?P<byte_exa>[0-9]*EB)",
                "%Z": "(?P<byte_zetta>[0-9]*ZB)",
                "%Y": "(?P<byte_yotta>[0-9]*YB)",
            },
            fmt.Storage.regex(),
        )

    def test_storage_formatter(self):
        formatter = fmt.Storage.formatter(storage=512)
        regex = fmt.Storage.regex()
        self.assertDictEqual(
            {
                "%b": {"regex": "(?P<bit>[0-9]*)", "value": "512"},
                "%B": {"regex": "(?P<byte>[0-9]*B)", "value": "64B"},
                "%K": {"regex": "(?P<byte_kilo>[0-9]*KB)", "value": "0KB"},
                "%M": {"regex": "(?P<byte_mega>[0-9]*MB)", "value": "0MB"},
                "%G": {"regex": "(?P<byte_giga>[0-9]*GB)", "value": "0GB"},
                "%T": {"regex": "(?P<byte_tera>[0-9]*TB)", "value": "0TB"},
                "%P": {"regex": "(?P<byte_peta>[0-9]*PB)", "value": "0PB"},
                "%E": {"regex": "(?P<byte_exa>[0-9]*EB)", "value": "0EB"},
                "%Z": {"regex": "(?P<byte_zetta>[0-9]*ZB)", "value": "0ZB"},
                "%Y": {"regex": "(?P<byte_yotta>[0-9]*YB)", "value": "0YB"},
            },
            {
                i: {
                    "regex": regex[i],
                    "value": fmt.caller(formatter[i]["value"]),
                }
                for i in formatter
            },
        )

    def test_storage_formatter_raise(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.Storage.formatter(1.23)
        self.assertTrue(
            "Storage formatter does not support for value, 1.23."
            in str(context.exception)
        )

    def test_storage_properties(self):
        self.assertEqual("<Storage.parse('10481', '%b')>", self.st.__repr__())
        self.assertEqual(hash(self.st.string), self.st.__hash__())

        self.assertEqual(82824, self.st_p.value)
        self.assertEqual("82824", self.st_p.string)

        self.assertEqual(135005, self.st_p2.value)
        self.assertEqual("135005", self.st_p2.string)

        self.assertEqual(0, self.st_default.value)
        self.assertEqual("0", self.st_default.string)

    def test_storage_format(self):
        self.assertEqual("82824", self.st_p.format("%b"))
        self.assertEqual("10353B", self.st_p.format("%B"))

        self.assertEqual("135005", self.st_p2.format("%b"))
        self.assertEqual("16876B", self.st_p2.format("%B"))
        self.assertEqual("16KB", self.st_p2.format("%K"))

        self.assertEqual("0", self.st_default.format("%b"))
        self.assertEqual("0B", self.st_default.format("%B"))

        with self.assertRaises(fmt.FormatterKeyError) as context:
            self.st_default.format("%A")
        self.assertTrue(
            "the format: '%A' does not support for 'Storage'"
            in str(context.exception)
        )

    def test_storage_order(self):
        self.assertTrue(self.st_p <= self.st_p2)
        self.assertTrue(self.st_p < self.st_p2)
        self.assertFalse(self.st_p == self.st_p2)
        self.assertFalse(self.st_p >= self.st_p2)
        self.assertFalse(self.st_p > self.st_p2)

    def test_level_compare(self):
        self.assertEqual(1, self.st_p.level.value)
        self.assertEqual(0, self.st_default.level.value)
        self.assertTrue(self.st_p.level == self.st_p2.level)
        self.assertFalse(self.st_default.level == self.st_p2.level)
        self.assertTrue(self.st_default.level < self.st_p2.level)
        self.assertListEqual([True], self.st_p.level.slot)
        self.assertListEqual([False], self.st_default.level.slot)
