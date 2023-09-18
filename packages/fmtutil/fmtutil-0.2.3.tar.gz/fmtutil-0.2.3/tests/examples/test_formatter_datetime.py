# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the formatter object examples for Datetime.
"""
import unittest
from datetime import datetime

import fmtutil.formatter as fmt


class DatetimeExampleTestCase(unittest.TestCase):
    def test_parse_examples(self):
        self.assertEqual(
            datetime(2021, 1, 1, microsecond=135000),
            fmt.Datetime.parse("2021-01-1 135043", "%Y-%m-%-d %f").value,
        )
        # FIXME: this datetime does not match with monday in this week
        self.assertEqual(
            datetime(2021, 1, 3),
            fmt.Datetime.parse("2021-Jan Monday 3", "%Y-%b %A %-d").value,
        )

    def test_format_example(self):
        dt = fmt.Datetime.parse(
            "20230917 23:08:56.041000", "%Y%m%d %H:%M:%S.%f"
        )
        self.assertEqual("2023", dt.format("%Y"))
        self.assertEqual("09", dt.format("%m"))
        self.assertEqual("9", dt.format("%-m"))
        self.assertEqual("17", dt.format("%d"))
        self.assertEqual("17", dt.format("%-d"))
        self.assertEqual("23", dt.format("%H"))
        self.assertEqual("23", dt.format("%-H"))
        self.assertEqual("08", dt.format("%M"))
        self.assertEqual("8", dt.format("%-M"))
        self.assertEqual("56", dt.format("%S"))
        self.assertEqual("56", dt.format("%-S"))
        self.assertEqual("041000", dt.format("%f"))
