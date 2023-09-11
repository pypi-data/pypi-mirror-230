# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the Datetime formatter object.
"""
import unittest
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

import fmtutil.formatter as fmt


class DatetimeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        """Set up Datetime instances with different parsing values."""
        self.maxDiff = None
        self.dt = fmt.Datetime(
            {"year": "2022", "month": "12", "day": "30", "second": "43"}
        )
        self.dt2 = fmt.Datetime(
            {
                "year": "2022",
                "weeks_year_sun_pad": "02",
                "week": "6",
            }
        )
        self.dt3 = fmt.Datetime({"weeks_year_mon_pad": "35"})
        self.dt_default = fmt.Datetime()
        self.dt_p = fmt.Datetime.parse("2021-01-1 135043", "%Y-%m-%-d %f")

    def test_datetime_formatter_raise(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.Datetime.formatter(date(2023, 1, 23))
        self.assertTrue(
            (
                "Datetime formatter does not support for value, "
                "datetime.date(2023, 1, 23)."
            )
            in str(context.exception)
        )

    def test_datetime_regex(self):
        self.assertDictEqual(
            {
                "%n": (
                    "(?P<year>\\d{4})"
                    "(?P<month_pad>01|02|03|04|05|06|07|08|09|10|11|12)"
                    "(?P<day_pad>[0-3][0-9])_(?P<hour_pad>[0-2][0-9])"
                    "(?P<minute_pad>[0-6][0-9])(?P<second_pad>[0-6][0-9])"
                ),
                "%Y": "(?P<year>\\d{4})",
                "%y": "(?P<year_cut_pad>\\d{2})",
                "%-y": "(?P<year_cut>\\d{1,2})",
                "%m": "(?P<month_pad>01|02|03|04|05|06|07|08|09|10|11|12)",
                "%-m": "(?P<month>1|2|3|4|5|6|7|8|9|10|11|12)",
                "%b": (
                    "(?P<month_short>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|"
                    "Nov|Dec)"
                ),
                "%B": (
                    "(?P<month_full>January|February|March|April|May|June|"
                    "July|August|September|October|November|December)"
                ),
                "%a": "(?P<week_shortname>Mon|Thu|Wed|Tue|Fri|Sat|Sun)",
                "%A": (
                    "(?P<week_fullname>Monday|Thursday|Wednesday|Tuesday|"
                    "Friday|Saturday|Sunday)"
                ),
                "%w": "(?P<week>[0-6])",
                "%u": "(?P<week_mon>[1-7])",
                "%d": "(?P<day_pad>[0-3][0-9])",
                "%-d": "(?P<day>\\d{1,2})",
                "%H": "(?P<hour_pad>[0-2][0-9])",
                "%-H": "(?P<hour>\\d{2})",
                "%I": "(?P<hour_12_pad>00|01|02|03|04|05|06|07|08|09|10|11|12)",
                "%-I": "(?P<hour_12>0|1|2|3|4|5|6|7|8|9|10|11|12)",
                "%M": "(?P<minute_pad>[0-6][0-9])",
                "%-M": "(?P<minute>\\d{1,2})",
                "%S": "(?P<second_pad>[0-6][0-9])",
                "%-S": "(?P<second>\\d{1,2})",
                "%j": "(?P<day_year_pad>[0-3][0-9][0-9])",
                "%-j": "(?P<day_year>\\d{1,3})",
                "%U": "(?P<weeks_year_sun_pad>[0-5][0-9])",
                "%W": "(?P<weeks_year_mon_pad>[0-5][0-9])",
                "%p": "(?P<local>PM|AM)",
                "%f": "(?P<microsecond_pad>\\d{6})",
            },
            fmt.Datetime.regex(),
        )

    def test_datetime_properties(self):
        self.assertEqual(
            (
                "<Datetime.parse("
                "'2022-12-30 00:00:43.000000', "
                "'%Y-%m-%d %H:%M:%S.%f')>"
            ),
            self.dt.__repr__(),
        )
        self.assertEqual("2022-12-30 00:00:43.000", self.dt.__str__())

        # Test `cls.string` property
        self.assertEqual("2022-12-30 00:00:43.000", self.dt.string)
        self.assertEqual("2022-01-15 00:00:00.000", self.dt2.string)
        self.assertEqual("1990-08-27 00:00:00.000", self.dt3.string)
        self.assertEqual("1990-01-01 00:00:00.000", self.dt_default.string)
        self.assertEqual("2021-01-01 00:00:00.135", self.dt_p.string)

        # Test `cls.value` property
        self.assertEqual(datetime(2022, 12, 30, second=43), self.dt.value)

        # Test static methods
        self.assertEqual("20", self.dt._from_day_year(value="50"))

        self.assertTrue(self.dt2.valid("20220115-00", "%Y%m%d-%S"))

    def test_datetime_parser(self):
        self.assertEqual(
            fmt.Datetime.parse("2021-01-01 20210101", "%Y-%m-%d %Y%m%d"),
            fmt.Datetime.parse("2021-01-01", "%Y-%m-%d"),
        )
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.Datetime.parse("2021-01-01 20220101", "%Y-%m-%d %Y%m%d")
        self.assertTrue(
            (
                "Parsing with some duplicate format name that have value "
                "do not all equal."
            )
            in str(context.exception)
        )

    def test_datetime_format(self):
        self.assertEqual(
            r"(\d{4})(01|02|03|04|05|06|07|08|09|10|11|12)([0-3][0-9])",
            fmt.Datetime.gen_format("%Y%m%d", alias=False),
        )
        self.assertEqual("22", self.dt.format("%-y"))
        self.assertEqual("19900101", self.dt_default.format("%Y%m%d"))

    def test_datetime_order(self):
        self.assertTrue(
            fmt.Datetime.parse("2021-01-1 135043", "%Y-%m-%-d %f")
            <= fmt.Datetime.parse("2021-01-2 135043", "%Y-%m-%-d %f")
        )
        self.assertFalse(
            fmt.Datetime.parse("2021-01-1 135043", "%Y-%m-%-d %f")
            > fmt.Datetime.parse("2021-01-2 135043", "%Y-%m-%-d %f")
        )

    def test_level_compare(self):
        self.assertListEqual(
            [False, False, False, False, False, True, True, True],
            self.dt2.level.slot,
        )
        self.assertEqual(21, self.dt2.level.value)
        self.assertListEqual(
            [True, False, False, False, False, True, True, True],
            self.dt_p.level.slot,
        )
        self.assertEqual(22, self.dt_p.level.value)

    def test_datetime_operation(self):
        # 2022-12-30 00:00:43 + 10 days
        self.assertEqual(
            datetime(2023, 1, 9, 0, 0, 43),
            (self.dt + relativedelta(days=10)).value,
        )

        # 2022-12-30 00:00:43 + 10 days
        self.assertEqual(
            datetime(2023, 1, 1, 10, 0, 43),
            (self.dt + timedelta(days=2, hours=10)).value,
        )

        # 2022-12-30 00:00:43 + 1 years + 1 months
        self.assertEqual(
            datetime(2024, 1, 30, 0, 0, 43),
            (relativedelta(years=1, months=1) + self.dt).value,
        )

        self.assertEqual(timedelta(days=349, seconds=43), (self.dt - self.dt2))

        # 2022-12-30 00:00:43 + 10 days
        self.assertEqual(
            datetime(2022, 12, 27, 14, 0, 43),
            (self.dt - timedelta(days=2, hours=10)).value,
        )

        with self.assertRaises(TypeError) as context:
            (self.dt + self.dt)
        self.assertEqual(
            "unsupported operand type(s) for +: 'Datetime' and 'Datetime'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (self.dt - 2)
        self.assertEqual(
            "unsupported operand type(s) for -: 'Datetime' and 'int'",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            (2 - self.dt)
        self.assertEqual(
            "unsupported operand type(s) for -: 'int' and 'Datetime'",
            str(context.exception),
        )
