# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the formatter group object examples.
"""
import unittest
from typing import List

import fmtutil.formatter as fmt


class FormatterGroupExampleTestCase(unittest.TestCase):
    def test_fmt_group_parse_examples(self):
        grouping: fmt.FormatterGroupType = fmt.make_group(
            {
                "naming": fmt.make_const(
                    fmt=fmt.Naming,
                    value="data_engineer",
                ),
                "domain": fmt.make_const(
                    fmt=fmt.Naming,
                    value="demo",
                ),
                "timestamp": fmt.Datetime,
            }
        )
        rs_parse: List[fmt.FormatterGroup] = []
        for filename in (
            "dataEngineer_demo_20230101.json",
            "dataEngineer_demo_20230226.json",
            "dataEngineer_demo_20230418.json",
            "dataEngineer_demo_20230211_temp.json",
            "dataEngineer_demo_20230101_bk.json",
        ):
            try:
                rs_parse.append(
                    grouping.parse(
                        filename,
                        "{naming:%c}_{domain:%s}_{timestamp:%Y%m%d}.json",
                    )
                )
            except fmt.FormatterGroupArgumentError:
                continue
        self.assertEqual("20230418", max(rs_parse).format("{timestamp:%Y%m%d}"))
        self.assertEqual("20230101", min(rs_parse).format("{timestamp:%Y%m%d}"))
