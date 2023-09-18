# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the Constant formatter object.
"""
import unittest

import fmtutil.formatter as fmt
from fmtutil.exceptions import FormatterValueError


class ConstantTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.const: fmt.ConstantType = fmt.make_const(
            name="NameConst",
            formatter={
                "%n": "normal",
                "%s": "special",
            },
        )
        self.const02: fmt.ConstantType = fmt.make_const(
            name="ExtensionConst",
            formatter={
                "%g": "gzip",
                "%-g": "gz",
                "%b": "bz2",
                "%r": "rar",
                "%x": "xz",
                "%z": "zip",
            },
        )
        self.const03: fmt.ConstantType = fmt.make_const(
            formatter=fmt.Naming(
                {
                    "shorts": "de",
                    "strings": "data engineer",
                }
            ),
        )
        self.const04: fmt.ConstantType = fmt.make_const(
            formatter=fmt.Serial.parse("199", "%n"),
        )
        self.const05: fmt.ConstantType = fmt.make_const(
            fmt=fmt.Naming,
            value=["data", "pipeline"],
        )

        self.const06: fmt.ConstantType = fmt.Serial.passer(2023).to_const()
        self.ct: fmt.Constant = self.const.parse("normal_life", "%n_life")
        self.ct02: fmt.Constant = self.const02.parse("gzip_life", "%g_life")
        self.ct03: fmt.Constant = self.const03.parse("data engineer", "%n")
        self.ct04: fmt.Constant = self.const04.parse("199", "%n")
        self.ct05: fmt.Constant = self.const05.parse("data_pipeline", "%s")
        self.ct06: fmt.Constant = self.const06.parse("11111100111", "%b")

    def test_const_init_empty_value(self):
        self.assertListEqual(
            [],
            fmt.make_const(fmt=fmt.Naming).parse("test", "test%n").value,
        )
        self.assertListEqual(
            ["1990"],
            fmt.make_const(fmt=fmt.Datetime).parse("D1990", "D%Y").value,
        )
        self.assertListEqual(
            ["0"],
            fmt.make_const(fmt=fmt.Version).parse("A0", "A%m").value,
        )
        self.assertListEqual(
            ["0"],
            fmt.make_const(fmt=fmt.Serial).parse("0_tt", "%n_tt").value,
        )
        self.assertListEqual(
            ["0B"],
            fmt.make_const(fmt=fmt.Storage).parse("0B_", "%B_").value,
        )

    def test_const_init_raise(self):
        with self.assertRaises(fmt.FormatterArgumentError) as context:
            fmt.make_const(name="DemoConst")
        self.assertTrue(
            (
                "with 'formatter', The Constant constructor function must pass "
                "formatter nor fmt arguments."
            )
            in str(context.exception)
        )
        with self.assertRaises(fmt.FormatterArgumentError) as context:
            fmt.make_const(formatter={"%n": "normal"})
        self.assertTrue(
            "with 'name', The Constant want name arguments"
            in str(context.exception)
        )

    def test_const_regex(self):
        self.assertDictEqual(
            {
                "%n": "(?P<november>normal)",
                "%s": "(?P<sierra>special)",
            },
            self.const.regex(),
        )
        self.assertDictEqual(
            {
                "%n": "(?P<november>data engineer)",
                "%N": "(?P<novemberupper>DATA ENGINEER)",
                "%-N": "(?P<novemberupperminus>Data Engineer)",
                "%u": "(?P<uniform>DATA ENGINEER)",
                "%l": "(?P<lima>data engineer)",
                "%t": "(?P<tango>Data Engineer)",
                "%a": "(?P<alpha>de)",
                "%A": "(?P<alphaupper>DE)",
                "%c": "(?P<charlie>dataEngineer)",
                "%-c": "(?P<charlieminus>DataEngineer)",
                "%p": "(?P<papa>DataEngineer)",
                "%k": "(?P<kilo>data-engineer)",
                "%K": "(?P<kiloupper>DATA-ENGINEER)",
                "%-K": "(?P<kiloupperminus>Data-Engineer)",
                "%f": "(?P<foxtrot>dataengineer)",
                "%F": "(?P<foxtrotupper>DATAENGINEER)",
                "%s": "(?P<sierra>data_engineer)",
                "%S": "(?P<sierraupper>DATA_ENGINEER)",
                "%-S": "(?P<sierraupperminus>Data_Engineer)",
                "%v": "(?P<victor>dtngnr)",
                "%V": "(?P<victorupper>DTNGNR)",
            },
            self.const03.regex(),
        )
        self.assertDictEqual(
            {
                "%n": "(?P<november>199)",
                "%p": "(?P<papa>199)",
                "%b": "(?P<bravo>11000111)",
            },
            self.const04.regex(),
        )

    def test_const_parser(self):
        self.assertEqual(
            self.ct.parse("normal_and_special", "%n_and_%s").value,
            ["normal", "special"],
        )

    def test_const_parser_raise(self):
        with self.assertRaises(FormatterValueError) as context:
            self.const.parse("special_job", "%s_life")
        self.assertTrue(
            (
                "value 'special_job' does not match "
                "with format '(?P<sierra__0>special)_life'"
            )
            in str(context.exception)
        )

    def test_const_properties(self):
        self.assertEqual(
            "<NameConst.parse('normal', '%n')>", self.ct.__repr__()
        )
        self.assertEqual(
            "<ExtensionConst.parse('gzip', '%g')>", self.ct02.__repr__()
        )
        self.assertEqual(
            "<NamingConst.parse('data engineer', '%n')>", self.ct03.__repr__()
        )
        self.assertEqual(
            "<SerialConst.parse('199', '%n')>", self.ct04.__repr__()
        )
        self.assertEqual(
            "<NamingConst.parse('data_pipeline', '%s')>", self.ct05.__repr__()
        )
        self.assertEqual(
            "<SerialConst.parse('11111100111', '%b')>", self.ct06.__repr__()
        )
        self.assertEqual(1, self.ct.level.value)
        self.assertEqual(["normal"], self.ct.value)
        self.assertEqual("normal", self.ct.string)
        self.assertEqual(["gzip"], self.ct02.value)
        self.assertEqual("gzip", self.ct02.string)
        self.assertEqual(["data engineer"], self.ct03.value)
        self.assertEqual("data engineer", self.ct03.string)
        self.assertEqual(hash(tuple(self.ct.value)), self.ct.__hash__())

    def test_const_format(self):
        self.assertEqual("special", self.ct.format("%s"))
        self.assertEqual("normal normal special", self.ct.format("%n %n %s"))

    def test_const_order(self):
        self.assertTrue(self.ct < self.ct02)
        self.assertTrue(self.ct > self.ct02)
        self.assertFalse(self.ct == "demo")

    def test_const_from_formatter_method(self):
        name_const = fmt.Naming.parse("data engineer", fmt="%n").to_const()
        self.assertEqual(
            "NamingConst",
            name_const.__name__,
        )
        self.assertEqual(
            "dtngnr", name_const.parse("data_engineer", fmt="%s").format("%v")
        )
